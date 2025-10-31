"""
E-KAY Platform - Admin Forms
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from ..models import User

class UserForm(FlaskForm):
    """Formulaire pour créer un nouvel utilisateur"""
    username = StringField('Nom d\'utilisateur', 
                         validators=[DataRequired(), 
                                   Length(min=3, max=50)])
    email = StringField('Email', 
                       validators=[DataRequired(), 
                                 Email(), 
                                 Length(max=120)])
    password = PasswordField('Mot de passe', 
                           validators=[DataRequired(), 
                                     Length(min=8, 
                                           message='Le mot de passe doit contenir au moins 8 caractères')])
    password_confirm = PasswordField('Confirmer le mot de passe', 
                                   validators=[DataRequired(), 
                                             EqualTo('password', 
                                                    message='Les mots de passe ne correspondent pas')])
    is_admin = BooleanField('Administrateur')
    is_landlord = BooleanField('Propriétaire')
    email_verified = BooleanField('Email vérifié')
    submit = SubmitField('Enregistrer')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ce nom d\'utilisateur est déjà utilisé. Veuillez en choisir un autre.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Cet email est déjà enregistré. Veuillez en utiliser un autre.')

class UserEditForm(FlaskForm):
    """Formulaire pour modifier un utilisateur existant"""
    username = StringField('Nom d\'utilisateur', 
                         validators=[DataRequired(), 
                                   Length(min=3, max=50)])
    email = StringField('Email', 
                       validators=[DataRequired(), 
                                 Email(), 
                                 Length(max=120)])
    password = PasswordField('Nouveau mot de passe',
                           validators=[Optional(),
                                     Length(min=8, 
                                           message='Le mot de passe doit contenir au moins 8 caractères')])
    password_confirm = PasswordField('Confirmer le mot de passe',
                                   validators=[EqualTo('password',
                                                     message='Les mots de passe ne correspondent pas')])
    is_admin = BooleanField('Administrateur')
    is_landlord = BooleanField('Propriétaire')
    email_verified = BooleanField('Email vérifié')
    submit = SubmitField('Mettre à jour')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Ce nom d\'utilisateur est déjà utilisé. Veuillez en choisir un autre.')
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Cet email est déjà enregistré. Veuillez en utiliser un autre.')

class PropertySearchForm(FlaskForm):
    """Formulaire de recherche pour les propriétés"""
    query = StringField('Rechercher', 
                       validators=[Optional()],
                       render_kw={"placeholder": "Rechercher par titre, ville, description..."})
    property_type = SelectField('Type de bien', 
                              choices=[('', 'Tous les types'), 
                                      ('house', 'Maison'), 
                                      ('apartment', 'Appartement'),
                                      ('room', 'Chambre'),
                                      ('other', 'Autre')],
                              validators=[Optional()])
    status = SelectField('Statut',
                        choices=[('', 'Tous les statuts'),
                                ('available', 'Disponible'),
                                ('unavailable', 'Non disponible')],
                        validators=[Optional()])
    submit = SubmitField('Filtrer')
