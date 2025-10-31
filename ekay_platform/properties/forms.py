from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (
    StringField, TextAreaField, DecimalField, IntegerField, 
    SelectField, SubmitField, DateField, BooleanField, 
    MultipleFileField, SelectMultipleField, HiddenField, 
    FieldList, FormField, Form as BaseForm
)
from wtforms.validators import (
    DataRequired, Length, NumberRange, Optional, 
    InputRequired, Email, ValidationError, AnyOf
)
from flask import current_app, request
from flask_babel import _, lazy_gettext as _l
from datetime import datetime, timedelta, timezone
import re
from urllib.parse import urlparse, urljoin
from werkzeug.utils import secure_filename
import os

# Fonction utilitaire pour la validation des URLs
def is_safe_url(target):
    """Vérifie qu'une URL est sûre pour la redirection"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

# Validateur personnalisé pour les fichiers images
def validate_image(form, field):
    if field.data:
        filename = secure_filename(field.data.filename)
        if not ('.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}):
            raise ValidationError(_('Format de fichier non supporté. Utilisez des images au format JPG, PNG ou WebP.'))

# Validateur pour les numéros de téléphone
def validate_phone_number(form, field):
    if field.data:
        phone_regex = r'^\+?[0-9\s\(\)\-]{8,20}$'
        if not re.match(phone_regex, field.data):
            raise ValidationError(_('Numéro de téléphone invalide. Utilisez le format international (ex: +509 36 12 3456)'))

# Validateur pour les prix
def validate_price(form, field):
    if field.data is not None and field.data < 0:
        raise ValidationError(_('Le prix ne peut pas être négatif'))
    # Vérifier que le prix est cohérent avec le type de transaction
    if hasattr(form, 'transaction_type') and form.transaction_type.data == 'sale' and field.data and field.data < 1000:
        raise ValidationError(_('Le prix de vente semble trop bas pour une propriété'))

# Validateur pour les dates de disponibilité
def validate_available_from(form, field):
    if field.data:
        if field.data < datetime.now().date():
            raise ValidationError(_('La date de disponibilité ne peut pas être dans le passé'))

# Validateur pour les coordonnées GPS
def validate_coordinates(form, field):
    if field.name == 'latitude' and form.latitude.data:
        try:
            lat = float(form.latitude.data)
            if not -90 <= lat <= 90:
                raise ValidationError(_('La latitude doit être comprise entre -90 et 90 degrés'))
        except ValueError:
            raise ValidationError(_('La latitude doit être un nombre valide'))
    
    if field.name == 'longitude' and form.longitude.data:
        try:
            lng = float(form.longitude.data)
            if not -180 <= lng <= 180:
                raise ValidationError(_('La longitude doit être comprise entre -180 et 180 degrés'))
        except ValueError:
            raise ValidationError(_('La longitude doit être un nombre valide'))

class ContactForm(FlaskForm):
    """Formulaire de contact pour les propriétés"""
    name = StringField(_l('Votre nom'), validators=[
        DataRequired(_l('Veuillez entrer votre nom')),
        Length(min=2, max=100, message=_l('Le nom doit contenir entre 2 et 100 caractères'))
    ])
    
    email = StringField(_l('Votre email'), validators=[
        DataRequired(_l('Veuillez entrer votre adresse email')),
        Email(_l('Veuillez entrer une adresse email valide'))
    ])
    
    phone = StringField(_l('Téléphone (optionnel)'), validators=[
        Optional(),
        Length(min=8, max=20, message=_l('Le numéro de téléphone doit contenir entre 8 et 20 caractères')),
    ])
    
    message = TextAreaField(_l('Votre message'), validators=[
        DataRequired(_l('Veuillez entrer votre message')),
        Length(min=10, max=2000, message=_l('Le message doit contenir entre 10 et 2000 caractères'))
    ], render_kw={
        'rows': 5,
        'placeholder': _l('Bonjour, je suis intéressé(e) par votre annonce...')
    })
    
    submit = SubmitField(_l('Envoyer le message'))
    
    def validate_phone(self, field):
        """Valide le format du numéro de téléphone"""
        if field.data and not re.match(r'^[0-9+()\-\s]+$', field.data):
            raise ValidationError(_l('Numéro de téléphone invalide. Utilisez uniquement des chiffres, espaces, +, - et ().'))


class PropertySearchForm(FlaskForm):
    """Formulaire de recherche de propriétés"""
    # Champ de recherche textuelle
    q = StringField(_l('Rechercher'), validators=[
        Optional(),
        Length(max=100, message=_l('La recherche ne peut pas dépasser 100 caractères'))
    ], render_kw={
        'placeholder': _l('Rechercher par mot-clé, ville, quartier...'),
        'class': 'form-control'
    })
    
    # Filtres de base
    property_type = SelectField(_l('Type de bien'), choices=[
        ('', _l('Tous les types')),
        ('house', _l('Maison')),
        ('apartment', _l('Appartement')),
        ('studio', _l('Studio')),
        ('villa', _l('Villa')),
        ('commercial', _l('Local commercial')),
        ('land', _l('Terrain'))
    ], validators=[Optional()], default='')
    
    min_price = DecimalField(_l('Prix min'), validators=[
        Optional(),
        NumberRange(min=0, message=_l('Le prix minimum doit être positif'))
    ], render_kw={
        'placeholder': _l('Min'),
        'min': '0',
        'step': '1000'
    })
    
    max_price = DecimalField(_l('Prix max'), validators=[
        Optional(),
        NumberRange(min=0, message=_l('Le prix maximum doit être positif'))
    ], render_kw={
        'placeholder': _l('Max'),
        'min': '0',
        'step': '1000'
    })
    
    # Filtres avancés
    min_rooms = IntegerField(_l('Pièces min'), validators=[
        Optional(),
        NumberRange(min=1, max=10, message=_l('Le nombre de pièces doit être entre 1 et 10'))
    ], default=0, render_kw={
        'min': '1',
        'max': '10'
    })
    
    min_bedrooms = IntegerField(_l('Chambres min'), validators=[
        Optional(),
        NumberRange(min=0, max=10, message=_l('Le nombre de chambres doit être entre 0 et 10'))
    ], default=0, render_kw={
        'min': '0',
        'max': '10'
    })
    
    min_bathrooms = IntegerField(_l('SDB min'), validators=[
        Optional(),
        NumberRange(min=0, max=10, message=_l('Le nombre de salles de bain doit être entre 0 et 10'))
    ], default=0, render_kw={
        'min': '0',
        'max': '10'
    })
    
    min_area = IntegerField(_l('Surface min (m²)'), validators=[
        Optional(),
        NumberRange(min=0, max=10000, message=_l('La surface doit être entre 0 et 10 000 m²'))
    ], render_kw={
        'min': '0',
        'max': '10000',
        'step': '1'
    })
    
    max_area = IntegerField(_l('Surface max (m²)'), validators=[
        Optional(),
        NumberRange(min=0, max=10000, message=_l('La surface doit être entre 0 et 10 000 m²'))
    ], render_kw={
        'min': '0',
        'max': '10000',
        'step': '1'
    })
    
    # Équipements
    has_kitchen = BooleanField(_('Cuisine équipée'))
    has_parking = BooleanField(_('Parking'))
    has_garden = BooleanField(_('Jardin'))
    has_balcony = BooleanField(_('Balcon/Terrasse'))
    has_pool = BooleanField(_('Piscine'))
    is_furnished = BooleanField(_('Meublé'))
    available_soon = BooleanField(_('Disponible rapidement'))
    
    # Tri
    sort_by = SelectField(_('Trier par'), choices=[
        ('newest', _('Plus récentes')),
        ('price_asc', _('Prix croissant')),
        ('price_desc', _('Prix décroissant')),
        ('area_desc', _('Plus grande surface'))
    ], default='newest')
    
    # Pagination
    page = HiddenField(default=1)
    
    def validate(self, extra_validators=None):
        """Validation personnalisée pour s'assurer que le prix min est inférieur au prix max"""
        if not super().validate():
            return False
            
        if self.min_price.data is not None and self.max_price.data is not None:
            if self.min_price.data > self.max_price.data:
                self.max_price.errors.append(_('Le prix maximum doit être supérieur au prix minimum'))
                return False
                
        return True


class LocationForm(BaseForm):
    """Sous-formulaire pour la localisation"""
    address = StringField(_l('Adresse complète *'), validators=[
        DataRequired(_l('L\'adresse est requise')),
        Length(max=300, message=_l('L\'adresse ne peut pas dépasser 300 caractères'))
    ], render_kw={
        'placeholder': _l('Ex: 123 Rue de la République'),
        'class': 'form-control',
        'data-controller': 'address-autocomplete',
        'data-action': 'input->address-autocomplete#search',
        'autocomplete': 'off'
    })
    
    city = StringField(_l('Ville *'), validators=[
        DataRequired(_l('La ville est requise')),
        Length(max=100, message=_l('Le nom de la ville ne peut pas dépasser 100 caractères'))
    ], render_kw={
        'placeholder': _l('Ex: Port-au-Prince'),
        'class': 'form-control',
        'data-address-autocomplete-target': 'city'
    })
    
    state = StringField(_l('Département/Région'), validators=[
        Optional(),
        Length(max=100, message=_l('Le nom du département ne peut pas dépasser 100 caractères'))
    ], render_kw={
        'placeholder': _l('Ex: Ouest'),
        'class': 'form-control',
        'data-address-autocomplete-target': 'state'
    })
    
    postal_code = StringField(_l('Code postal'), validators=[
        Optional(),
        Length(max=20, message=_l('Le code postal ne peut pas dépasser 20 caractères'))
    ], render_kw={
        'placeholder': _l('Ex: 6110'),
        'class': 'form-control',
        'data-address-autocomplete-target': 'postalCode'
    })
    
    country = StringField(_l('Pays *'), validators=[
        DataRequired(_l('Le pays est requis')),
        Length(max=100, message=_l('Le nom du pays ne peut pas dépasser 100 caractères'))
    ], default='Haïti', render_kw={
        'class': 'form-control',
        'data-address-autocomplete-target': 'country'
    })
    
    # Coordonnées GPS (cachées, remplies par JavaScript)
    latitude = HiddenField(validators=[Optional(), validate_coordinates])
    longitude = HiddenField(validators=[Optional(), validate_coordinates])


class PriceForm(BaseForm):
    """Sous-formulaire pour les informations de prix"""
    price_type = SelectField(_l('Type de prix *'), 
        choices=[
            ('monthly', _('Prix mensuel')), 
            ('annual', _('Prix annuel'))
        ],
        default='monthly',
        render_kw={
            'class': 'form-select',
            'data-action': 'change->price-calculator#togglePriceType'
        }
    )
    
    price = DecimalField(_l('Montant *'), validators=[
        DataRequired(_l('Le prix est requis')),
        NumberRange(min=0, message=_l('Le prix doit être positif')),
        validate_price
    ], render_kw={
        'step': '0.01',
        'min': '0',
        'placeholder': _l('Ex: 150000'),
        'class': 'form-control-lg text-end',
        'data-price-type': 'monthly',
        'data-action': 'input->price-calculator#updatePrice'
    })
    
    # Champ caché pour stocker l'autre type de prix
    alternate_price = HiddenField()
    
    currency = SelectField(_l('Devise *'), validators=[
        DataRequired(_l('La devise est requise'))
    ], choices=[
        ('HTG', 'HTG - Gourde Haïtienne'),
        ('USD', 'USD - Dollar Américain'),
        ('EUR', 'EUR - Euro')
    ], default='USD', render_kw={
        'class': 'form-select'
    })
    
    price_period = SelectField(_l('Période'), validators=[
        Optional()
    ], choices=[
        ('', _('Prix total')),
        ('day', _('Par jour')),
        ('week', _('Par semaine')),
        ('month', _('Par mois')),
        ('year', _('Par an'))
    ], render_kw={
        'class': 'form-select',
        'data-action': 'change->price-calculator#updatePeriod'
    })
    
    security_deposit = DecimalField(_('Caution (si location)'), validators=[
        Optional(),
        NumberRange(min=0, message=_('La caution doit être positive ou zéro'))
    ], default=0, render_kw={
        'step': '0.01',
        'min': '0',
        'placeholder': _('Ex: 500'),
        'class': 'form-control',
        'data-price-calculator-target': 'deposit'
    })
    
    includes_utilities = BooleanField(_('Charges comprises'), default=False, render_kw={
        'data-action': 'change->price-calculator#toggleUtilities'
    })
    
    utilities_cost = DecimalField(_('Coût des charges'), validators=[
        Optional(),
        NumberRange(min=0, message=_('Le coût doit être positif ou zéro'))
    ], default=0, render_kw={
        'step': '0.01',
        'min': '0',
        'class': 'form-control',
        'data-price-calculator-target': 'utilitiesCost',
        'disabled': True
    })


class PropertyForm(FlaskForm):
    """Formulaire pour créer ou modifier une propriété"""
    # Section: Informations de base
    title = StringField(_l('Titre de l\'annonce *'), validators=[
        DataRequired(_l('Le titre est requis')), 
        Length(min=5, max=100, message=_l('Le titre doit faire entre 5 et 100 caractères'))
    ], render_kw={
        'placeholder': _l('Ex: Magnifique appartement 3 pièces avec vue mer'),
        'class': 'form-control-lg'
    })
    
    # Intégration de PriceForm
    price_info = FormField(PriceForm, label='Informations de prix')
    
    description = TextAreaField(_l('Description détaillée *'), validators=[
        DataRequired(_l('La description est requise')), 
        Length(min=10, message=_l('La description doit faire au moins 10 caractères'))
    ], render_kw={
        'rows': 8,
        'placeholder': _l('Décrivez votre bien en détail : localisation, commodités à proximité, état du bien, etc.'),
        'class': 'form-control',
        'data-controller': 'textarea-autogrow'
    })
    
    # Type et catégorie
    property_type = SelectField(_l('Type de bien *'), validators=[
        DataRequired(_l('Le type de bien est requis'))
    ], choices=[
        ('house', _('Maison')),
        ('apartment', _('Appartement')),
        ('villa', _('Villa')),
        ('land', _('Terrain')),
        ('commercial', _('Local commercial')),
        ('office', _('Bureau')),
        ('warehouse', _('Entrepôt')),
        ('other', _('Autre'))
    ], render_kw={
        'class': 'form-select'
    })
    
    transaction_type = SelectField(_l('Type de transaction *'), validators=[
        DataRequired(_l('Le type de transaction est requis'))
    ], choices=[
        ('sale', _('À vendre')),
        ('rent', _('À louer')),
        ('vacation_rental', _('Location saisonnière'))
    ], render_kw={
        'class': 'form-select'
    })
    
    # Caractéristiques principales
    
    area = IntegerField(_l('Surface (m²) *'), validators=[
        DataRequired(_l('La surface est requise')),
        NumberRange(min=1, message=_l('La surface doit être supérieure à 0'))
    ], render_kw={
        'min': '1',
        'placeholder': _l('Ex: 120')
    })
    
    rooms = IntegerField(_l('Nombre de pièces *'), validators=[
        DataRequired(_l('Le nombre de pièces est requis')),
        NumberRange(min=0, message=_l('Le nombre de pièces doit être positif ou zéro'))
    ], render_kw={
        'min': '0',
        'placeholder': _l('Ex: 3')
    })
    
    bedrooms = IntegerField(_l('Chambres'), validators=[
        Optional(),
        NumberRange(min=0, message=_l('Le nombre de chambres doit être positif ou zéro'))
    ], render_kw={
        'min': '0',
        'placeholder': _l('Ex: 2')
    })
    
    bathrooms = IntegerField(_l('Salles de bain'), validators=[
        Optional(),
        NumberRange(min=0, message=_l('Le nombre de salles de bain doit être positif ou zéro'))
    ], render_kw={
        'min': '0',
        'placeholder': _l('Ex: 1')
    })
    
    # Informations de localisation
    address = StringField(_l('Adresse complète *'), validators=[
        DataRequired(_l('L\'adresse est requise')),
        Length(max=300, message=_l('L\'adresse ne peut pas dépasser 300 caractères'))
    ], render_kw={
        'placeholder': _l('Ex: 123 Rue de la République'),
        'class': 'form-control',
        'data-controller': 'address-autocomplete'
    })
    
    city = StringField(_l('Ville *'), validators=[
        DataRequired(_l('La ville est requise')),
        Length(max=100, message=_l('Le nom de la ville ne peut pas dépasser 100 caractères'))
    ], render_kw={
        'placeholder': _l('Ex: Port-au-Prince'),
        'class': 'form-control'
    })
    
    state = StringField(_l('Département/Région'), validators=[
        Optional(),
        Length(max=100, message=_l('Le nom du département ne peut pas dépasser 100 caractères'))
    ], render_kw={
        'placeholder': _l('Ex: Ouest'),
        'class': 'form-control'
    })
    
    postal_code = StringField(_l('Code postal'), validators=[
        Optional(),
        Length(max=20, message=_l('Le code postal ne peut pas dépasser 20 caractères'))
    ], render_kw={
        'placeholder': _l('Ex: 6110'),
        'class': 'form-control'
    })
    
    country = StringField(_l('Pays *'), validators=[
        DataRequired(_l('Le pays est requis')),
        Length(max=100, message=_l('Le nom du pays ne peut pas dépasser 100 caractères'))
    ], default='Haïti', render_kw={
        'class': 'form-control'
    })
    
    # Coordonnées GPS (cachées, remplies par JavaScript)
    latitude = HiddenField(validators=[Optional()])
    longitude = HiddenField(validators=[Optional()])
    
    # Caractéristiques supplémentaires
    year_built = IntegerField(_l('Année de construction'), validators=[
        Optional(),
        NumberRange(min=1000, max=2100, message=_l('Veuillez entrer une année valide'))
    ], render_kw={
        'min': '1000',
        'max': '2100',
        'placeholder': _l('Ex: 2010')
    })
    
    floor = IntegerField(_l('Étage'), validators=[
        Optional(),
        NumberRange(min=-5, max=200, message=_l('L\'étage doit être entre -5 et 200'))
    ], render_kw={
        'min': '-5',
        'max': '200',
        'placeholder': _l('Ex: 2')
    })
    
    total_floors = IntegerField(_l('Nombre total d\'étages'), validators=[
        Optional(),
        NumberRange(min=1, message=_l('Le nombre d\'étages doit être d\'au moins 1'))
    ], render_kw={
        'min': '1',
        'placeholder': _l('Ex: 3')
    })
    
    # Équipements et commodités
    has_kitchen = BooleanField(_('Cuisine équipée'), default=False)
    has_parking = BooleanField(_('Parking'), default=False)
    has_garden = BooleanField(_('Jardin'), default=False)
    has_balcony = BooleanField(_('Balcon/Terrasse'), default=False)
    has_pool = BooleanField(_('Piscine'), default=False)
    has_elevator = BooleanField(_('Ascenseur'), default=False)
    has_air_conditioning = BooleanField(_('Climatisation'), default=False)
    has_heating = BooleanField(_('Chauffage'), default=False)
    is_furnished = BooleanField(_('Meublé'), default=False)
    is_new_construction = BooleanField(_('Neuf'), default=False)
    
    # Informations supplémentaires
    is_featured = BooleanField(_('Mettre en avant cette annonce'), default=False)
    is_premium = BooleanField(_('Annonce premium'), default=False)
    
    # Champ de caution déplacé dans PriceForm
    
    available_from = DateField(_('Disponible à partir du'), validators=[
        Optional()
    ], format='%Y-%m-%d', render_kw={
        'type': 'date',
        'min': datetime.now().strftime('%Y-%m-%d')
    })
    
    minimum_rent_days = IntegerField(_('Durée minimale de location (jours)'), 
        validators=[
            Optional(),
            NumberRange(min=1, message=_('La durée minimale doit être d\'au moins 1 jour'))
        ], default=1, render_kw={
            'min': '1',
            'placeholder': _('Ex: 30')
        }
    )
    
    # Règles et conditions
    allows_pets = BooleanField(_('Animaux acceptés'), default=False)
    allows_smoking = BooleanField(_('Fumeurs acceptés'), default=False)
    allows_events = BooleanField(_('Événements autorisés'), default=False)
    
    # Informations de contact
    contact_name = StringField(_('Nom du contact'), validators=[
        Optional(),
        Length(max=100, message=_('Le nom ne peut pas dépasser 100 caractères'))
    ], render_kw={
        'placeholder': _('Ex: Jean Dupont')
    })
    
    contact_phone = StringField(_('Téléphone du contact'), validators=[
        Optional(),
        Length(max=20, message=_('Le numéro de téléphone ne peut pas dépasser 20 caractères'))
    ], render_kw={
        'placeholder': _('Ex: +509 36 12 3456')
    })
    
    contact_email = StringField(_('Email du contact'), validators=[
        Optional(),
        Email(_('Veuillez entrer une adresse email valide')),
        Length(max=120, message=_('L\'email ne peut pas dépasser 120 caractères'))
    ], render_kw={
        'placeholder': _('exemple@domaine.com')
    })
    
    # Champs cachés
    user_id = HiddenField()
    status = SelectField(_('Statut'), choices=[
        ('draft', _('Brouillon')),
        ('pending', _('En attente de validation')),
        ('published', _('Publié')),
        ('sold', _('Vendu')),
        ('rented', _('Loué')),
        ('archived', _('Archivé'))
    ], default='draft', render_kw={
        'class': 'form-select'
    })
    
    # Boutons d'action
    save_draft = SubmitField(_('Enregistrer comme brouillon'), render_kw={
        'class': 'btn btn-outline-secondary',
        'name': 'action',
        'value': 'save_draft'
    })
    
    submit_for_review = SubmitField(_('Publier l\'annonce'), render_kw={
        'class': 'btn btn-primary',
        'name': 'action',
        'value': 'submit_for_review'
    })
    
    # Méthodes de validation personnalisées
    def validate(self, extra_validators=None):
        """Validation personnalisée pour les champs interdépendants"""
        # Validation standard du formulaire
        if not super().validate():
            return False
            
        # Vérification de la cohérence entre le type de transaction et le prix
        if self.transaction_type.data in ['rent', 'vacation_rental'] and not self.available_from.data:
            self.available_from.errors.append(_('La date de disponibilité est requise pour les locations'))
            return False
            
        # Vérification des coordonnées GPS
        if not self.latitude.data or not self.longitude.data:
            # Essayer de géocoder l'adresse si les coordonnées ne sont pas fournies
            try:
                from geopy.geocoders import Nominatim
                from geopy.exc import GeocoderUnavailable, GeocoderTimedOut
                
                geolocator = Nominatim(user_agent="ekay_platform")
                address = f"{self.address.data}, {self.postal_code.data} {self.city.data}, {self.country.data}"
                location = geolocator.geocode(address, timeout=10)
                
                if location:
                    self.latitude.data = location.latitude
                    self.longitude.data = location.longitude
                else:
                    self.address.errors.append(_('Impossible de localiser cette adresse. Veuillez vérifier les informations ou ajouter manuellement les coordonnées GPS.'))
                    return False
                    
            except (GeocoderUnavailable, GeocoderTimedOut):
                # On ne bloque pas si le service de géocodage est indisponible
                pass
                
        # Vérification des images (au moins une image requise pour la publication)
        if hasattr(self, 'images') and not self.images.data and self.status.data == 'published':
            self.images.errors.append(_('Au moins une image est requise pour publier une annonce'))
            return False
            
        return True
    
    def populate_obj(self, obj):
        """Surcharge pour gérer correctement les champs personnalisés"""
        super().populate_obj(obj)
        
        # Gestion des champs de localisation imbriqués
        if hasattr(self, 'location'):
            for field in self.location:
                setattr(obj, field.name, field.data)
                
        # Gestion des champs de prix imbriqués
        if hasattr(self, 'pricing'):
            for field in self.pricing:
                if field.name != 'price_period':  # Ne pas enregistrer le champ de période dans la base
                    setattr(obj, field.name, field.data)
    
    def process(self, formdata=None, obj=None, **kwargs):
        """Traitement personnalisé des données du formulaire"""
        # Appel à la méthode parente
        super().process(formdata, obj, **kwargs)
        
        # Initialisation des champs imbriqués si nécessaire
        if obj:
            # Initialisation des champs de localisation
            if hasattr(self, 'location'):
                for field in self.location:
                    field.data = getattr(obj, field.name, None)
                    
            # Initialisation des champs de prix
            if hasattr(self, 'pricing'):
                for field in self.pricing:
                    field.data = getattr(obj, field.name, None)
    
    # Méthodes utilitaires
    def get_field_translations(self):
        """Retourne les traductions des libellés des champs pour le JavaScript"""
        return {
            'required_field': _('Ce champ est requis'),
            'invalid_email': _('Veuillez entrer une adresse email valide'),
            'invalid_phone': _('Numéro de téléphone invalide'),
            'invalid_number': _('Veuillez entrer un nombre valide'),
            'invalid_date': _('Date invalide'),
            'date_in_past': _('La date ne peut pas être dans le passé'),
            'min_value': _('La valeur doit être supérieure ou égale à {min}'),
            'max_value': _('La valeur doit être inférieure ou égale à {max}'),
            'min_length': _('Le texte doit contenir au moins {min} caractères'),
            'max_length': _('Le texte ne peut pas dépasser {max} caractères')
        }

    state = StringField(_l('Département'), validators=[
        Length(max=100, message=_l('Le nom du département ne peut pas dépasser 100 caractères'))
    ], render_kw={
        'placeholder': _l('Ex: Ouest')
    })
    
    country = StringField(_l('Pays *'), validators=[
        DataRequired(_l('Le pays est requis')),
        Length(max=100, message=_l('Le nom du pays ne peut pas dépasser 100 caractères'))
    ], default='Haïti')
    
    # Informations sur le bien
    property_type = SelectField(_l('Type de bien *'), 
        choices=[
            ('house', _('Maison')),
            ('apartment', _('Appartement')),
            ('studio', _('Studio')),
            ('villa', _('Villa')),
            ('commercial', _('Local commercial')),
            ('land', _('Terrain'))
        ],
        validators=[DataRequired(_l('Veuillez sélectionner un type de bien'))],
        render_kw={
            'class': 'form-select'
        }
    )
    
    price = DecimalField(_l('Prix mensuel (HTG) *'), validators=[
        DataRequired(_l('Le prix est requis')), 
        NumberRange(min=0, message=_l('Le prix doit être un nombre positif'))
    ], render_kw={
        'min': '0',
        'step': '1000',
        'placeholder': _l('Ex: 50000')
    })
    
    annual_price = DecimalField(_l('Prix annuel (HTG, optionnel)'), validators=[
        Optional(), 
        NumberRange(min=0, message=_l('Le prix doit être un nombre positif'))
    ], render_kw={
        'min': '0',
        'step': '1000',
        'placeholder': _l('Ex: 600000')
    })
    
    rooms = SelectField(_('Nombre de pièces *'), 
        choices=[
            (1, _('1 pièce (Studio)')),
            (2, _('2 pièces (T2)')),
            (3, _('3 pièces (T3)')),
            (4, _('4 pièces (T4)')),
            (5, _('5 pièces ou plus (T5+)'))
        ],
        coerce=int,
        validators=[DataRequired(_l('Veuillez sélectionner le nombre de pièces'))],
        render_kw={
            'class': 'form-select'
        }
    )
    
    bedrooms = IntegerField(_('Nombre de chambres'), validators=[
        NumberRange(min=0, max=50, message=_('Le nombre de chambres doit être entre 0 et 50')),
        Optional()
    ], render_kw={
        'min': '0',
        'max': '50',
        'placeholder': _l('Ex: 2')
    })
    
    bathrooms = IntegerField(_('Nombre de salles de bain *'), validators=[
        NumberRange(min=0, max=20, message=_('Le nombre de salles de bain doit être entre 0 et 20')),
        DataRequired(_l('Veuillez spécifier le nombre de salles de bain'))
    ], default=1, render_kw={
        'min': '0',
        'max': '20',
        'placeholder': _l('Ex: 1')
    })
    
    area = IntegerField(_('Superficie (m²) *'), validators=[
        NumberRange(min=1, max=100000, message=_('La superficie doit être entre 1 et 100 000 m²')),
        DataRequired(_l('Veuillez spécifier la superficie'))
    ], render_kw={
        'min': '1',
        'max': '100000',
        'step': '1',
        'placeholder': _l('Ex: 80')
    })
    
    # Équipements
    has_kitchen = BooleanField(_('Cuisine équipée'))
    has_parking = BooleanField(_('Parking'))
    has_garden = BooleanField(_('Jardin'))
    has_balcony = BooleanField(_('Balcon/Terrasse'))
    has_pool = BooleanField(_('Piscine'))
    is_furnished = BooleanField(_('Meublé'))
    
    # Disponibilité
    is_available = BooleanField(_('Ce bien est disponible à la location'), default=True)
    
    available_from = DateField(_('Disponible à partir du *'), 
        format='%Y-%m-%d',
        default=lambda: datetime.now(timezone.utc),
        validators=[InputRequired(_l('Veuillez spécifier une date de disponibilité'))],
        render_kw={
            'min': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            'max': (datetime.now(timezone.utc) + timedelta(days=365)).strftime('%Y-%m-%d')
        }
    )
    
    min_stay = SelectField(_('Durée minimale de location *'), 
        choices=[
            (1, _('1 mois')),
            (3, _('3 mois')),
            (6, _('6 mois')),
            (12, _('1 an')),
            (24, _('2 ans'))
        ],
        coerce=int,
        default=12,
        validators=[DataRequired(_('Veuillez sélectionner une durée minimale de location'))],
        render_kw={
            'class': 'form-select'
        }
    )
    
    # Options supplémentaires
    is_featured = BooleanField(_('Mettre en avant cette annonce (supplément)'))
    
    # Images
    images = MultipleFileField(_('Photos de la propriété *'), validators=[
        FileRequired(_('Veuillez télécharger au moins une photo')),
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], _l('Formats d\'image acceptés : JPG, PNG, WebP'))
    ], render_kw={
        'accept': 'image/*',
        'multiple': True
    })
    
    submit = SubmitField(_l('Publier l\'annonce'), render_kw={
        'class': 'btn btn-primary btn-lg w-100'
    })
    
    def __init__(self, *args, **kwargs):
        super(PropertyForm, self).__init__(*args, **kwargs)
        
        # Personnalisation des classes CSS pour les champs
        for field in self:
            if field.type not in ('SubmitField', 'CSRFTokenField', 'HiddenField'):
                if field.type == 'BooleanField':
                    field.render_kw = field.render_kw or {}
                    field.render_kw.update({'class': 'form-check-input'})
                elif field.type == 'TextAreaField':
                    field.render_kw = field.render_kw or {}
                    field.render_kw.update({'class': 'form-control', 'style': 'resize: vertical;'})
                elif field.type != 'SubmitField':
                    field.render_kw = field.render_kw or {}
                    field.render_kw.update({'class': 'form-control'})


class PropertyImageForm(FlaskForm):
    """Formulaire pour le téléchargement d'images de propriété"""
    images = MultipleFileField(_('Images du bien'), 
        validators=[
            FileRequired(_('Veuillez sélectionner au moins une image')),
            FileAllowed(
                ['jpg', 'jpeg', 'png', 'webp'], 
                _('Formats acceptés : JPG, JPEG, PNG, WebP')
            )
        ],
        render_kw={
            'accept': 'image/jpeg, image/png, image/webp',
            'multiple': True
        }
    )
    
    is_primary = BooleanField(_('Définir comme image principale'), default=True)
    
    submit = SubmitField(_('Télécharger les images'))
    
    def __init__(self, *args, **kwargs):
        super(PropertyImageForm, self).__init__(*args, **kwargs)
        
    def validate_images(self, field):
        """Valide les images téléchargées"""
        if field.data:
            for file in field.data:
                if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    raise ValidationError(_('Format de fichier non supporté. Utilisez JPG, PNG ou WebP.'))
                
                # Vérifier la taille du fichier (max 5MB)
                file.seek(0, 2)  # Aller à la fin du fichier
                file_size = file.tell()
                file.seek(0)  # Revenir au début du fichier
                
                if file_size > 5 * 1024 * 1024:  # 5MB
                    raise ValidationError(_('La taille maximale d\'une image est de 5 Mo.'))
