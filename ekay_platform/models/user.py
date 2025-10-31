"""
E-KAY Platform - User Model
Copyright (c) 2025 Walny Mardoché JULMICE. All Rights Reserved.

This software is proprietary and confidential.
Unauthorized copying, distribution, or use is strictly prohibited.
Contact: julmicemardoche@gmail.com
"""

from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from ..extensions import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20))
    is_landlord = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False, server_default='0')
    email_verified_at = db.Column(db.DateTime, nullable=True)
    reset_password_token = db.Column(db.String(100), unique=True)
    reset_password_expires = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    properties = db.relationship('Property', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Property', secondary='favorites', lazy='dynamic',
                              backref=db.backref('favorited_by', lazy='dynamic'))
    tokens = db.relationship('Token', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if 'password' in kwargs:
            self.password = kwargs['password']
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Vérifie si le mot de passe fourni correspond au hash stocké"""
        return check_password_hash(self.password_hash, password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def ping(self):
        """Mettre à jour le timestamp de dernière activité"""
        self.last_seen = datetime.now(timezone.utc)
        db.session.add(self)
        db.session.commit()
    
    def generate_auth_token(self, token_type, expires_in=3600):
        """Génère un token d'authentification"""
        from .tokens import Token
        # Invalider les anciens tokens du même type
        Token.query.filter_by(user_id=self.id, token_type=token_type, used=False).update({'used': True})
        
        # Créer un nouveau token
        token = Token(user_id=self.id, token_type=token_type, expires_in=expires_in)
        db.session.add(token)
        db.session.commit()
        return token
    
    def verify_token(self, token, token_type):
        """Vérifie si un token est valide"""
        from .tokens import Token
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
        if not self.email_verified_at:
            self.email_verified_at = datetime.now(timezone.utc)
        db.session.add(self)
        db.session.commit()
    
    def can(self, permission):
        """Vérifie les permissions de l'utilisateur"""
        if self.is_admin:
            return True
        if permission == 'landlord' and self.is_landlord:
            return True
        return False
    
    def avatar_url(self, size=100):
        """Génère une URL d'avatar avec Gravatar"""
        import hashlib
        email = self.email or ''  # Utiliser une chaîne vide si email est None
        digest = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    
    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
