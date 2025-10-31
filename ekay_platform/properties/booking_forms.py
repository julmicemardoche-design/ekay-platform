"""
E-KAY Platform - Booking Forms
"""

from flask_wtf import FlaskForm
from wtforms import DateField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Optional, ValidationError
from datetime import date, datetime

class BookingForm(FlaskForm):
    """Formulaire de réservation d'une propriété"""
    start_date = DateField(
        'Date d\'arrivée',
        validators=[DataRequired(message="La date d'arrivée est requise")],
        format='%Y-%m-%d',
        render_kw={
            'class': 'form-control datepicker',
            'min': date.today().strftime('%Y-%m-%d'),
            'autocomplete': 'off'
        }
    )
    
    end_date = DateField(
        'Date de départ',
        validators=[DataRequired(message="La date de départ est requise")],
        format='%Y-%m-%d',
        render_kw={
            'class': 'form-control datepicker',
            'min': date.today().strftime('%Y-%m-%d'),
            'autocomplete': 'off'
        }
    )
    
    guests = IntegerField(
        'Nombre de voyageurs',
        validators=[DataRequired(message="Veuillez indiquer le nombre de voyageurs")],
        default=1,
        render_kw={
            'min': 1,
            'class': 'form-control'
        }
    )
    
    notes = TextAreaField(
        'Demandes spéciales',
        validators=[Optional()],
        render_kw={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Avez-vous des demandes particulières ?'
        }
    )
    
    submit = SubmitField(
        'Réserver maintenant',
        render_kw={'class': 'btn btn-primary btn-lg w-100'}
    )
    
    def validate_end_date(self, field):
        if field.data <= self.start_date.data:
            raise ValidationError('La date de fin doit être postérieure à la date de début.')
        
        if (field.data - self.start_date.data).days > 365:
            raise ValidationError('La durée de séjour ne peut pas dépasser un an.')
    
    def validate_start_date(self, field):
        if field.data < date.today():
            raise ValidationError('La date d\'arrivée ne peut pas être dans le passé.')
    
    def validate_guests(self, field):
        if field.data < 1:
            raise ValidationError('Le nombre de voyageurs doit être d\'au moins 1.')
