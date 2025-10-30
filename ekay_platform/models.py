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

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20))
    is_landlord = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    properties = db.relationship('Property', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Property', secondary='favorites', lazy='dynamic',
                              backref=db.backref('favorited_by', lazy='dynamic'))
    
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
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    rooms = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(300), nullable=False)
    corridor = db.Column(db.String(50))
    color = db.Column(db.String(50))
    is_available = db.Column(db.Boolean, default=True)
    available_from = db.Column(db.DateTime, default=datetime.utcnow)
    min_stay = db.Column(db.Integer, default=12)  # in months
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    images = db.relationship('PropertyImage', backref='property', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Property {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'rooms': self.rooms,
            'address': self.address,
            'corridor': self.corridor,
            'color': self.color,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() + 'Z',
            'owner': self.owner.username,
            'image': self.images.first().filename if self.images.first() else None
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
