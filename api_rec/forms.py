from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, Regexp
from api_rec.models import User, Data
from flask_login import current_user
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from flask_uploads import DATA, UploadSet
import re


def my_val(form, field):
    
    if field.data[:2] != '01' :
        raise ValidationError('Egyptain Phone Number Please')
    if len(field.data) != 11 :
        raise ValidationError('not real numbe')

def space_re(form, field):
    data = field.data.lstrip()
    if len(data) < 3 :
        raise ValidationError('Recuired att least 3 letters')

    return field.data



class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), 
                           Length(min=3, max=30),
                           space_re])
    email = EmailField('Email',
                        validators=[DataRequired(), 
                        Email()])
    phone = StringField('Phone', validators=[Optional(), my_val])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=30),space_re])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

    def validate_phone(self, phone):
        phone = User.query.filter_by(phone=phone.data).first()
        if phone:
            raise ValidationError('That phone is taken. Please choose a different one.')



class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(),
    Length(min=8, max=30)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), 
                           Length(min=2, max=30),
                           space_re])
    email = StringField('Email',
                        validators=[DataRequired(), 
                        Email()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
    

    def validate_email(self, email):
            if email.data != current_user.email:
                user = User.query.filter_by(email=email.data).first()
                if user:
                    raise ValidationError('That email is taken. Please choose a different one.')


data = UploadSet('data', DATA)


class PostForm(FlaskForm):
    name = StringField('Name',validators=[DataRequired(),
    space_re])
    data_url = StringField('Project Link',validators=[DataRequired(), Regexp('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')])
    submit = SubmitField('submit')

    def validate_name(self, name):
        data = Data.query.filter_by(data_name=name.data).first()

        if data :
            raise ValidationError('That name is taken. Please choose a different one.')


class UpdataPostForm(FlaskForm):
    name = StringField('Name',validators=[DataRequired(),
    space_re])
    data_url = StringField('Project Link',validators=[DataRequired(), Regexp('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')])
    submit = SubmitField('submit')

    def validate_name(self, name):

        cur =  current_user.Data.with_entities(Data.data_name).all()

        data = Data.query.with_entities(Data.data_name).first()

        if data :
            if data not in cur :
                raise ValidationError('this name is taken')


