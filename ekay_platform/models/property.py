"""
E-KAY Platform - Property Model
Copyright (c) 2025 Walny Mardoché JULMICE. All Rights Reserved.

This software is proprietary and confidential.
Unauthorized copying, distribution, or use is strictly prohibited.
Contact: julmicemardoche@gmail.com
"""

from datetime import datetime, timezone
import os
import uuid
from flask import current_app, url_for
from ..extensions import db

class Property(db.Model):
    """Modèle pour les propriétés à louer"""
    __tablename__ = 'properties'
    
    # Identifiant et statut
    id = db.Column(db.Integer, primary_key=True)
    is_available = db.Column(db.Boolean, default=True, index=True)
    is_featured = db.Column(db.Boolean, default=False, index=True)
    
    # Informations de base
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    property_type = db.Column(db.String(50), nullable=False, default='apartment', index=True)
    
    # Prix
    price = db.Column(db.Float, nullable=False, index=True)  # Prix mensuel en HTG
    annual_price = db.Column(db.Float, nullable=True)  # Prix annuel en HTG (optionnel)
    price_type = db.Column(db.String(10), default='monthly', nullable=False, index=True)  # 'monthly' ou 'annual'
    
    # Détails du bien
    rooms = db.Column(db.Integer, nullable=False, index=True)  # Nombre total de pièces
    bedrooms = db.Column(db.Integer, nullable=True, index=True)  # Nombre de chambres
    bathrooms = db.Column(db.Integer, nullable=True, default=1)  # Nombre de salles de bain
    area = db.Column(db.Float, nullable=True, index=True)  # Superficie en m²
    
    # Caractéristiques
    has_kitchen = db.Column(db.Boolean, default=False, index=True)
    has_parking = db.Column(db.Boolean, default=False, index=True)
    has_garden = db.Column(db.Boolean, default=False, index=True)
    has_balcony = db.Column(db.Boolean, default=False, index=True)
    has_pool = db.Column(db.Boolean, default=False, index=True)
    is_furnished = db.Column(db.Boolean, default=False, index=True)
    
    # Localisation
    address = db.Column(db.String(300), nullable=False, index=True)
    city = db.Column(db.String(100), nullable=False, index=True)
    state = db.Column(db.String(100), nullable=True, index=True)
    country = db.Column(db.String(100), nullable=False, default='Haiti', index=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    # Disponibilité
    available_from = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    min_stay = db.Column(db.Integer, default=12)  # Durée minimale de location en mois
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    view_count = db.Column(db.Integer, default=0)  # Nombre de vues
    
    # Anciens champs à supprimer après migration
    corridor = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    
    # Clé étrangère vers l'utilisateur propriétaire
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relations
    images = db.relationship('PropertyImage', backref='property', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Property {self.title}>'
    
    def get_primary_image(self):
        """Retourne l'image principale de la propriété"""
        return self.images.filter_by(is_primary=True).first() or self.images.first()
    
    def get_image_url(self, image, size='medium'):
        """Génère l'URL d'une image avec la taille spécifiée"""
        if not image:
            return url_for('static', filename='images/placeholder-property.jpg')
        
        # Gestion des différentes tailles d'images
        base, ext = os.path.splitext(image.filename)
        if size == 'thumbnail':
            filename = f"{base}_thumb{ext}"
        elif size == 'large':
            filename = f"{base}_large{ext}"
        else:  # medium par défaut
            filename = image.filename
            
        return url_for('static', filename=f'uploads/properties/{self.id}/{filename}')
    
    def increment_views(self):
        """Incrémente le compteur de vues"""
        self.view_count = Property.view_count + 1
        db.session.add(self)
        db.session.commit()
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire pour JSON"""
        primary_image = self.get_primary_image()
        
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'property_type': self.property_type,
            'price': self.price,
            'annual_price': self.annual_price,
            'rooms': self.rooms,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'area': self.area,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'is_available': self.is_available,
            'is_featured': self.is_featured,
            'has_kitchen': self.has_kitchen,
            'has_parking': self.has_parking,
            'has_garden': self.has_garden,
            'has_balcony': self.has_balcony,
            'has_pool': self.has_pool,
            'is_furnished': self.is_furnished,
            'available_from': self.available_from.isoformat() if self.available_from else None,
            'min_stay': self.min_stay,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'view_count': self.view_count,
            'image_url': self.get_image_url(primary_image) if primary_image else None,
            'is_available': self.is_available,
            'available_from': self.available_from.isoformat() if self.available_from else None,
            'min_stay': self.min_stay,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id,
            'images': [img.filename for img in self.images.all()]
        }


class PropertyImage(db.Model):
    """Modèle pour les images des propriétés"""
    __tablename__ = 'property_images'
    
    # Tailles d'images prédéfinies (largeur, hauteur)
    THUMBNAIL_SIZE = (300, 200)
    MEDIUM_SIZE = (800, 600)
    LARGE_SIZE = (1200, 900)
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)  # Taille en octets
    content_type = db.Column(db.String(50))  # Type MIME
    width = db.Column(db.Integer)  # Largeur de l'image originale
    height = db.Column(db.Integer)  # Hauteur de l'image originale
    is_primary = db.Column(db.Boolean, default=False, index=True)
    position = db.Column(db.Integer, default=0)  # Position dans la galerie
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False, index=True)
    
    def __repr__(self):
        return f'<PropertyImage {self.filename}>'
    
    @property
    def path(self):
        """Retourne le chemin complet du fichier"""
        return os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            'properties',
            str(self.property_id),
            self.filename
        )
    
    @classmethod
    def get_upload_path(cls, property_id, filename):
        """Génère le chemin de sauvegarde pour un fichier uploadé"""
        # Créer un nom de fichier unique
        ext = filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Créer le répertoire s'il n'existe pas
        upload_dir = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            'properties',
            str(property_id)
        )
        os.makedirs(upload_dir, exist_ok=True)
        
        return os.path.join(upload_dir, filename)
    
    def create_thumbnail(self):
        """Crée une miniature de l'image"""
        return self._resize_image(*self.THUMBNAIL_SIZE, 'thumb')
    
    def create_medium(self):
        """Crée une version moyenne de l'image"""
        return self._resize_image(*self.MEDIUM_SIZE, 'medium')
    
    def create_large(self):
        """Crée une version grande de l'image"""
        return self._resize_image(*self.LARGE_SIZE, 'large')
    
    def _resize_image(self, width, height, suffix):
        """Redimensionne l'image à la taille spécifiée"""
        try:
            from PIL import Image
            import io
            
            # Ouvrir l'image originale
            img = Image.open(self.path)
            
            # Calculer les nouvelles dimensions en conservant le ratio
            img_ratio = img.width / img.height
            target_ratio = width / height
            
            if img_ratio > target_ratio:
                # L'image est plus large que la cible
                new_width = int(height * img_ratio)
                new_height = height
            else:
                # L'image est plus haute que la cible
                new_width = width
                new_height = int(width / img_ratio)
            
            # Redimensionner l'image
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Découper l'image pour qu'elle corresponde aux dimensions cibles
            left = (new_width - width) / 2
            top = (new_height - height) / 2
            right = (new_width + width) / 2
            bottom = (new_height + height) / 2
            img = img.crop((left, top, right, bottom))
            
            # Sauvegarder l'image redimensionnée
            base, ext = os.path.splitext(self.filename)
            new_filename = f"{base}_{suffix}{ext}"
            new_path = os.path.join(os.path.dirname(self.path), new_filename)
            
            # Convertir en mode RVB si nécessaire (pour les PNG avec canal alpha)
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            
            # Sauvegarder avec une qualité optimale
            img.save(new_path, 'JPEG', quality=85, optimize=True)
            
            return new_filename
            
        except Exception as e:
            current_app.logger.error(f"Erreur lors du redimensionnement de l'image: {e}")
            return None
    
    def delete_files(self):
        """Supprime tous les fichiers associés à cette image"""
        try:
            # Supprimer l'image originale et ses variantes
            for size in ['', '_thumb', '_medium', '_large']:
                base, ext = os.path.splitext(self.filename)
                filename = f"{base}{size}{ext}"
                filepath = os.path.join(
                    os.path.dirname(self.path),
                    filename
                )
                if os.path.exists(filepath):
                    os.remove(filepath)
            return True
        except Exception as e:
            current_app.logger.error(f"Erreur lors de la suppression des fichiers: {e}")
            return False
