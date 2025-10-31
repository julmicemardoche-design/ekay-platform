"""
E-KAY Platform - Database Models
Copyright (c) 2025 Walny Mardoché JULMICE. All Rights Reserved.

This software is proprietary and confidential.
Unauthorized copying, distribution, or use is strictly prohibited.
Contact: julmicemardoche@gmail.com
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager
from .models.tokens import Token

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20))
    is_landlord = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    email_verified_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    properties = db.relationship('Property', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Property', secondary='favorites', lazy='dynamic',
                              backref=db.backref('favorited_by', lazy='dynamic'))
    tokens = db.relationship('Token', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
    
    def generate_auth_token(self, token_type, expires_in=3600):
        """Génère un token d'authentification"""
        # Invalider les anciens tokens du même type
        Token.query.filter_by(user_id=self.id, token_type=token_type, used=False).update({'used': True})
        
        # Créer un nouveau token
        token = Token(user_id=self.id, token_type=token_type, expires_in=expires_in)
        db.session.add(token)
        db.session.commit()
        return token
    
    def verify_token(self, token, token_type):
        """Vérifie si un token est valide"""
        token = Token.query.filter_by(
            token=token, 
            user_id=self.id, 
            token_type=token_type,
            used=False
        ).first()
        
        if token and token.is_valid():
            token.mark_as_used()
            return True
        return False
    
    def verify_email(self):
        """Marque l'email comme vérifié"""
        self.email_verified = True
        self.email_verified_at = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
    
    def can(self, permission):
        if self.is_admin:
            return True
        if permission == 'landlord' and self.is_landlord:
            return True
        return False
    
    def __repr__(self):
        return f'<User {self.username}>'


class Property(db.Model):
    __tablename__ = 'properties'
    
    # Identifiant et informations de base
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    property_type = db.Column(db.String(50), nullable=False)  # house, apartment, villa, etc.
    transaction_type = db.Column(db.String(20), nullable=False)  # sale, rent, vacation_rental
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')  # HTG, USD, EUR
    area = db.Column(db.Float)  # Surface en m²
    rooms = db.Column(db.Integer, nullable=False)
    bedrooms = db.Column(db.Integer, default=0)
    bathrooms = db.Column(db.Float, default=1.0)  # Peut être un demi (1.5)
    floor = db.Column(db.Integer)  # Étage
    total_floors = db.Column(db.Integer)  # Nombre total d'étages du bâtiment
    year_built = db.Column(db.Integer)  # Année de construction
    
    # Adresse
    address = db.Column(db.String(300), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100), default='Haïti')
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Caractéristiques principales
    has_kitchen = db.Column(db.Boolean, default=False)
    has_parking = db.Column(db.Boolean, default=False)
    has_garden = db.Column(db.Boolean, default=False)
    has_balcony = db.Column(db.Boolean, default=False)
    has_pool = db.Column(db.Boolean, default=False)
    has_elevator = db.Column(db.Boolean, default=False)
    has_air_conditioning = db.Column(db.Boolean, default=False)
    has_heating = db.Column(db.Boolean, default=False)
    is_furnished = db.Column(db.Boolean, default=False)
    is_new_construction = db.Column(db.Boolean, default=False)
    
    # Détails supplémentaires
    security_deposit = db.Column(db.Float)  # Caution
    available_from = db.Column(db.DateTime, default=datetime.utcnow)
    minimum_rent_days = db.Column(db.Integer, default=1)  # Pour les locations
    
    # Règles
    allows_pets = db.Column(db.Boolean, default=False)
    allows_smoking = db.Column(db.Boolean, default=False)
    allows_events = db.Column(db.Boolean, default=False)
    
    # Informations de contact
    contact_name = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(120))
    
    # Statut et métadonnées
    status = db.Column(db.String(20), default='draft')  # draft, pending, published, sold, rented, archived
    is_featured = db.Column(db.Boolean, default=False)
    is_premium = db.Column(db.Boolean, default=False)
    views = db.Column(db.Integer, default=0)
    
    # Horodatage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # Clés étrangères
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relations
    images = db.relationship('PropertyImage', backref='property', lazy='dynamic', cascade='all, delete-orphan')
    
    # Champs supplémentaires pour les équipements
    has_wardrobes = db.Column(db.Boolean, default=False)
    has_dishwasher = db.Column(db.Boolean, default=False)
    has_washing_machine = db.Column(db.Boolean, default=False)
    has_dryer = db.Column(db.Boolean, default=False)
    has_tv = db.Column(db.Boolean, default=False)
    has_internet = db.Column(db.Boolean, default=False)
    has_terrace = db.Column(db.Boolean, default=False)
    has_security = db.Column(db.Boolean, default=False)
    has_intercom = db.Column(db.Boolean, default=False)
    has_caretaker = db.Column(db.Boolean, default=False)
    has_gym = db.Column(db.Boolean, default=False)
    has_doorman = db.Column(db.Boolean, default=False)
    has_pet_friendly = db.Column(db.Boolean, default=False)
    has_wheelchair_access = db.Column(db.Boolean, default=False)
    has_concierge = db.Column(db.Boolean, default=False)
    has_laundry = db.Column(db.Boolean, default=False)
    has_storage = db.Column(db.Boolean, default=False)
    has_covered_parking = db.Column(db.Boolean, default=False)
    has_garage = db.Column(db.Boolean, default=False)
    has_private_garden = db.Column(db.Boolean, default=False)
    has_shared_garden = db.Column(db.Boolean, default=False)
    has_roof_terrace = db.Column(db.Boolean, default=False)
    has_balcony_terrace = db.Column(db.Boolean, default=False)
    has_sea_view = db.Column(db.Boolean, default=False)
    has_mountain_view = db.Column(db.Boolean, default=False)
    has_city_view = db.Column(db.Boolean, default=False)
    has_pool_view = db.Column(db.Boolean, default=False)
    
    # Champs pour les détails de construction
    construction_year = db.Column(db.Integer)
    land_area = db.Column(db.Float)  # Surface du terrain en m²
    furnishing_type = db.Column(db.String(50))  # meublé, semi-meublé, vide
    condition = db.Column(db.String(50))  # neuf, bon état, à rénover, etc.
    orientation = db.Column(db.String(50))  # nord, sud, est, ouest
    view = db.Column(db.String(100))  # mer, montagne, ville, piscine, etc.
    heating_type = db.Column(db.String(50))  # électrique, gaz, fioul, etc.
    energy_efficiency_rating = db.Column(db.String(2))  # A, B, C, D, E, F, G
    
    def __repr__(self):
        return f'<Property {self.title}>'
    
    def to_dict(self):
        """Convertit l'objet Property en dictionnaire pour la sérialisation JSON"""
        # Gestion des images
        images_list = []
        if hasattr(self, 'images'):
            try:
                images_list = [{
                    'id': img.id,
                    'filename': img.filename,
                    'is_primary': img.is_primary,
                    'created_at': img.created_at.isoformat() + 'Z' if img.created_at else None
                } for img in self.images.all()]
            except Exception:
                images_list = []
        
        # Gestion du propriétaire
        owner_dict = None
        if hasattr(self, 'owner') and self.owner is not None:
            owner_dict = {
                'id': self.owner.id,
                'username': self.owner.username,
                'email': self.owner.email,
                'phone': getattr(self.owner, 'phone', None)
            }
        
        # Gestion de l'image principale
        main_image = None
        if hasattr(self, 'images'):
            try:
                primary_img = self.images.filter_by(is_primary=True).first()
                if primary_img:
                    main_image = primary_img.filename
                else:
                    first_img = self.images.first()
                    if first_img:
                        main_image = first_img.filename
            except Exception:
                pass
        
        return {
            # Informations de base
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'property_type': self.property_type,
            'transaction_type': self.transaction_type,
            'price': float(self.price) if self.price is not None else None,
            'currency': self.currency,
            'area': float(self.area) if self.area is not None else None,
            'rooms': self.rooms,
            'bedrooms': self.bedrooms,
            'bathrooms': float(self.bathrooms) if self.bathrooms is not None else None,
            'floor': self.floor,
            'total_floors': self.total_floors,
            'year_built': self.year_built,
            
            # Adresse
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country,
            'latitude': float(self.latitude) if self.latitude is not None else None,
            'longitude': float(self.longitude) if self.longitude is not None else None,
            
            # Caractéristiques principales
            'has_kitchen': bool(self.has_kitchen),
            'has_parking': bool(self.has_parking),
            'has_garden': bool(self.has_garden),
            'has_balcony': bool(self.has_balcony),
            'has_pool': bool(self.has_pool),
            'has_elevator': bool(self.has_elevator),
            'has_air_conditioning': bool(self.has_air_conditioning),
            'has_heating': bool(self.has_heating),
            'is_furnished': bool(self.is_furnished),
            'is_new_construction': bool(self.is_new_construction),
            
            # Détails supplémentaires
            'security_deposit': float(self.security_deposit) if self.security_deposit is not None else None,
            'available_from': self.available_from.isoformat() if self.available_from else None,
            'minimum_rent_days': self.minimum_rent_days,
            
            # Règles
            'allows_pets': bool(self.allows_pets),
            'allows_smoking': bool(self.allows_smoking),
            'allows_events': bool(self.allows_events),
            
            # Informations de contact
            'contact_name': self.contact_name,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            
            # Statut et métadonnées
            'status': self.status,
            'is_featured': bool(self.is_featured),
            'is_premium': bool(self.is_premium),
            'views': self.views,
            
            # Horodatage
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
            'published_at': self.published_at.isoformat() + 'Z' if self.published_at else None,
            
            # Propriétaire
            'owner': owner_dict,
            
            # Images
            'images': images_list,
            'image': main_image,
            
            # Champs supplémentaires pour les équipements
            'equipment': {
                'has_wardrobes': self.has_wardrobes,
                'has_dishwasher': self.has_dishwasher,
                'has_washing_machine': self.has_washing_machine,
                'has_dryer': self.has_dryer,
                'has_tv': self.has_tv,
                'has_internet': self.has_internet,
                'has_terrace': self.has_terrace,
                'has_security': self.has_security,
                'has_intercom': self.has_intercom,
                'has_caretaker': self.has_caretaker,
                'has_gym': self.has_gym,
                'has_doorman': self.has_doorman,
                'has_pet_friendly': self.has_pet_friendly,
                'has_wheelchair_access': self.has_wheelchair_access,
                'has_concierge': self.has_concierge,
                'has_laundry': self.has_laundry,
                'has_storage': self.has_storage,
                'has_covered_parking': self.has_covered_parking,
                'has_garage': self.has_garage,
                'has_private_garden': self.has_private_garden,
                'has_shared_garden': self.has_shared_garden,
                'has_roof_terrace': self.has_roof_terrace,
                'has_balcony_terrace': self.has_balcony_terrace,
                'has_sea_view': self.has_sea_view,
                'has_mountain_view': self.has_mountain_view,
                'has_city_view': self.has_city_view,
                'has_pool_view': self.has_pool_view
            },
            
            # Détails de construction
            'construction': {
                'construction_year': self.construction_year,
                'land_area': self.land_area,
                'furnishing_type': self.furnishing_type,
                'condition': self.condition,
                'orientation': self.orientation,
                'view': self.view,
                'heating_type': self.heating_type,
                'energy_efficiency_rating': self.energy_efficiency_rating
            }
        }


class PropertyImage(db.Model):
    __tablename__ = 'property_images'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)


# Association table for many-to-many relationship between users and favorite properties
favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('property_id', db.Integer, db.ForeignKey('properties.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
