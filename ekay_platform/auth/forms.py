from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, NumberRange, Regexp
import re
from ..models import User

class LoginForm(FlaskForm):
    username = StringField('Nom d\'utilisateur ou Email', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')


class RegistrationForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[
        DataRequired(),
        Length(min=3, max=64, message='Le nom d\'utilisateur doit contenir entre 3 et 64 caractères')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Veuillez entrer une adresse email valide')
    ])
    phone = StringField('Téléphone', validators=[
        DataRequired(),
        Length(min=8, max=20, message='Numéro de téléphone invalide')
    ])
    password = PasswordField('Mot de passe', validators=[
        DataRequired(message='Un mot de passe est requis'),
        Length(min=12, message='Le mot de passe doit contenir au moins 12 caractères'),
        Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$',
            message='Le mot de passe doit contenir au moins une majuscule, une minuscule, un chiffre et un caractère spécial (@$!%*?&)'
        )
    ],
    render_kw={
        'pattern': '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$',
        'title': '12 caractères minimum, avec majuscule, minuscule, chiffre et caractère spécial',
        'autocomplete': 'new-password'
    })
    password2 = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(),
        EqualTo('password', message='Les mots de passe ne correspondent pas')
    ])
    is_landlord = BooleanField('Je suis propriétaire et je souhaite publier des annonces')
    submit = SubmitField('S\'inscrire')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Ce nom d\'utilisateur est déjà utilisé. Veuillez en choisir un autre.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Cette adresse email est déjà utilisée. Utilisez une autre adresse ou connectez-vous.')
            
    def validate_password(self, field):
        # Vérifier que le mot de passe n'est pas trop courant
        common_passwords = [
            'password', '12345678', 'qwerty', 'azerty', '123456789',
            'password1', 'azerty123', 'motdepasse', '1234567890', 'qwerty123',
            '12345678910', 'azertyuiop', 'azerty1234', 'password123', 'azerty12345'
        ]
        
        if field.data.lower() in common_passwords:
            raise ValidationError('Ce mot de passe est trop commun. Veuillez en choisir un plus complexe.')
        
        # Vérifier que le mot de passe ne contient pas d'informations personnelles
        user_data = [self.email.data.lower(), self.username.data.lower()]
        
        for data in user_data:
            if data and len(data) > 2 and data in field.data.lower():
                raise ValidationError('Votre mot de passe ne doit pas contenir votre nom d\'utilisateur ou votre email')
                
        # Vérifier la complexité du mot de passe
        if not re.search(r'[A-Z]', field.data):
            raise ValidationError('Le mot de passe doit contenir au moins une lettre majuscule')
            
        if not re.search(r'[a-z]', field.data):
            raise ValidationError('Le mot de passe doit contenir au moins une lettre minuscule')
            
        if not re.search(r'\d', field.data):
            raise ValidationError('Le mot de passe doit contenir au moins un chiffre')
            
        if not re.search(r'[@$!%*?&]', field.data):
            raise ValidationError('Le mot de passe doit contenir au moins un caractère spécial (@$!%*?&)')


class EditProfileForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[
        DataRequired(),
        Length(min=3, max=64)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    phone = StringField('Téléphone', validators=[
        DataRequired(),
        Length(min=8, max=20)
    ])
    about_me = TextAreaField('À propos de moi', validators=[Length(min=0, max=500)])
    submit = SubmitField('Enregistrer les modifications')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Ce nom d\'utilisateur est déjà utilisé.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Cette adresse email est déjà utilisée.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Demander la réinitialisation du mot de passe')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nouveau mot de passe', validators=[
        DataRequired(message='Un mot de passe est requis'),
        Length(min=12, message='Le mot de passe doit contenir au moins 12 caractères'),
        Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$',
            message='Le mot de passe doit contenir au moins une majuscule, une minuscule, un chiffre et un caractère spécial (@$!%*?&)'
        )
    ],
    render_kw={
        'pattern': '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$',
        'title': '12 caractères minimum, avec majuscule, minuscule, chiffre et caractère spécial',
        'autocomplete': 'new-password'
    })
    
    password2 = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(message='Veuillez confirmer votre mot de passe'),
        EqualTo('password', message='Les mots de passe ne correspondent pas')
    ],
    render_kw={
        'autocomplete': 'new-password'
    })
    
    submit = SubmitField('Réinitialiser le mot de passe')
    
    def validate_password(self, field):
        # Vérifier que le mot de passe n'est pas trop courant
        common_passwords = [
            'password', '12345678', 'qwerty', 'azerty', '123456789',
            'password1', 'azerty123', 'motdepasse', '1234567890', 'qwerty123'
        ]
        
        if field.data.lower() in common_passwords:
            raise ValidationError('Ce mot de passe est trop commun. Veuillez en choisir un plus complexe.')
        
        # Vérifier que le mot de passe ne contient pas d'informations personnelles
        user_data = [self._fields.get('email', '').data.lower(), 
                    self._fields.get('username', '').data.lower()]
        
        for data in user_data:
            if data and len(data) > 2 and data in field.data.lower():
                raise ValidationError('Votre mot de passe ne doit pas contenir votre nom d\'utilisateur ou votre email')


class PropertyForm(FlaskForm):
    title = StringField('Titre de l\'annonce *', validators=[
        DataRequired(),
        Length(max=200, message='Le titre ne peut pas dépasser 200 caractères')
    ])
    village = StringField('Village *', default='La Différence', validators=[
        DataRequired(),
        Length(max=100, message='Le nom du village ne peut pas dépasser 100 caractères')
    ])
    latitude = StringField('Latitude *', validators=[
        DataRequired(),
        Length(max=20, message='Coordonnée invalide')
    ])
    longitude = StringField('Longitude *', validators=[
        DataRequired(),
        Length(max=20, message='Coordonnée invalide')
    ])
    description = TextAreaField('Description détaillée', validators=[
        Length(max=2000, message='La description ne peut pas dépasser 2000 caractères')
    ])
    price = IntegerField('Prix mensuel (HTG) *', validators=[
        DataRequired(),
        NumberRange(min=0, message='Le prix doit être un nombre positif')
    ])
    annual_price = IntegerField('Prix annuel (HTG, optionnel)', validators=[
        Optional(),
        NumberRange(min=0, message='Le prix ne peut pas être négatif')
    ])
    rooms = SelectField('Nombre de chambres *', coerce=int, choices=[
        (1, '1 chambre (Studio)'),
        (2, '2 chambres (T2)'),
        (3, '3 chambres (T3)'),
        (4, '4 chambres ou plus (T4+)')
    ], validators=[DataRequired()])
    address = StringField('Adresse complète *', validators=[
        DataRequired(),
        Length(max=300)
    ])
    corridor = StringField('Couloir', validators=[
        Length(max=50)
    ])
    color = StringField('Couleur de la maison', validators=[
        Length(max=50)
    ])
    is_available = BooleanField('Ce bien est disponible à la location', default=True)
    available_from = StringField('Disponible à partir du *', validators=[DataRequired()])
    min_stay = SelectField('Durée minimale de location *', coerce=int, choices=[
        (1, '1 mois'),
        (3, '3 mois'),
        (6, '6 mois'),
        (12, '1 an'),
        (24, '2 ans')
    ], default=12, validators=[DataRequired()])
    submit = SubmitField('Publier l\'annonce')
