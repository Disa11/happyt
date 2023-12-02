from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired,NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import FloatField


class DispenserForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired()])
    city = SelectField('City', coerce=int)
    country = SelectField('Country', coerce=int)
    breed = SelectField('Breed', coerce=int)
    species = SelectField('Species', coerce=int)
    age = IntegerField('Age', validators=[NumberRange(min=0)])
    #la ip del dispositivo hasheada
    code = StringField('Dispenser Code') 
    latitude = FloatField('latitude')
    longitude = FloatField('longitude')
    location_name = StringField('Location Name') 
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Log in')
    
    
class RegissterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    mail = StringField('Email', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    confirm_password = StringField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')
    
class UserLinksForm(FlaskForm):
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Solo se permiten imágenes.')])
    twitter_link = StringField('Twitter Link')
    facebook_link = StringField('Facebook Link')
    submit = SubmitField('Submit')