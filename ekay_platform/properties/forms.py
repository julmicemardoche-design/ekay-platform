from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import MultipleFileField
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class PropertyForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10)])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State/Province')
    country = StringField('Country', validators=[DataRequired()])
    property_type = SelectField('Property Type', 
                              choices=[
                                  ('house', 'House'),
                                  ('apartment', 'Apartment'),
                                  ('land', 'Land'),
                                  ('commercial', 'Commercial')
                              ],
                              validators=[DataRequired()])
    bedrooms = IntegerField('Bedrooms', validators=[NumberRange(min=0)])
    bathrooms = IntegerField('Bathrooms', validators=[NumberRange(min=0)])
    area = IntegerField('Area (sq ft)', validators=[NumberRange(min=0)])
    submit = SubmitField('Submit')

class PropertyImageForm(FlaskForm):
    images = MultipleFileField('Property Images', 
                             validators=[
                                 FileRequired('Please select at least one image'),
                                 FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only! (jpg, jpeg, png, gif)')
                             ])
    submit = SubmitField('Upload Images')
