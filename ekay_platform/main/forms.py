from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    SubmitField,
    DecimalField,
    IntegerField,
    BooleanField,
    FileField,
    FloatField
)
from wtforms.validators import DataRequired, Optional, NumberRange, Email, Length, InputRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.utils import secure_filename

class SearchForm(FlaskForm):
    """Form for property search"""
    min_price = DecimalField(
        'Prix minimum',
        validators=[Optional(), NumberRange(min=0)],
        places=0
    )
    
    max_price = DecimalField(
        'Prix maximum',
        validators=[Optional(), NumberRange(min=0)],
        places=0
    )
    
    rooms = SelectField(
        'Nombre de pièces',
        choices=[
            ('', 'Tous'),
            (1, '1 pièce'),
            (2, '2 pièces'),
            (3, '3 pièces'),
            (4, '4 pièces ou plus')
        ],
        validators=[Optional()],
        coerce=lambda x: int(x) if x else None
    )
    
    property_type = SelectField(
        'Type de bien',
        choices=[
            ('', 'Tous les types'),
            ('apartment', 'Appartement'),
            ('house', 'Maison'),
            ('room', 'Chambre')
        ],
        validators=[Optional()]
    )
    
    submit = SubmitField('Rechercher')


class ContactForm(FlaskForm):
    """Form for contact page"""
    name = StringField('Nom complet', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Sujet', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Envoyer le message')


class PropertyForm(FlaskForm):
    """Form for adding/editing properties"""
    title = StringField('Titre', validators=[DataRequired('Le titre est obligatoire')])
    description = TextAreaField('Description', validators=[DataRequired('La description est obligatoire')])
    price = DecimalField('Prix mensuel', validators=[
        DataRequired('Le prix est obligatoire'), 
        NumberRange(min=0, message='Le prix doit être positif')
    ])
    annual_price = DecimalField('Prix annuel (optionnel)', validators=[
        Optional(), 
        NumberRange(min=0, message='Le prix doit être positif')
    ])
    rooms = IntegerField('Nombre de pièces', validators=[
        DataRequired('Le nombre de pièces est obligatoire'),
        NumberRange(min=1, message='Le nombre de pièces doit être d\'au moins 1')
    ])
    address = StringField('Adresse', validators=[DataRequired('L\'adresse est obligatoire')])
    corridor = StringField('Couloir (optionnel)')
    village = StringField('Village', default='La Différence, Caracol')
    color = StringField('Couleur (code hexadécimal)')
    latitude = FloatField('Latitude', default=19.6917)
    longitude = FloatField('Longitude', default=-71.8250)
    is_available = BooleanField('Disponible', default=True)
    images = FileField('Images (plusieurs possibles)', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images uniquement (JPG, PNG)')
    ], render_kw={"multiple": True})
    submit = SubmitField('Enregistrer')
