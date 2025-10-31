"""
E-KAY Platform - Booking Model
"""

from datetime import datetime, timezone
from ..extensions import db

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending', 
                      nullable=False)  # pending, confirmed, cancelled, completed
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    notes = db.Column(db.Text)
    
    # Relations
    property = db.relationship('Property', backref='bookings')
    user = db.relationship('User', backref='bookings')
    
    def __repr__(self):
        return f'<Booking {self.id} - Property {self.property_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'property_id': self.property_id,
            'user_id': self.user_id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'notes': self.notes
        }
