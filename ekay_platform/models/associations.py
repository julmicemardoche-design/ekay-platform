"""
E-KAY Platform - Association Tables
"""

from ..extensions import db

# Table d'association pour les favoris
favorites = db.Table(
    'favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('property_id', db.Integer, db.ForeignKey('properties.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=db.func.current_timestamp())
)
