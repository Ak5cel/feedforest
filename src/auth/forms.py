from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField,
                     SubmitField)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')


class SignupForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=3, max=30)])
    email = StringField('Email',
                        validators=[DataRequired(), Email(message='Not a valid email address')])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=10, max=50)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class RequestPasswordResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email(message='Not a valid email address')])
    submit = SubmitField('Send Reset Request')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No account found with that email. Please signup first.')


class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password',
                             validators=[DataRequired(), 
                             Length(min=10, max=50, message='Password must be 10-50 characters long.')])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password', message='The two passwords do not match.')])
    submit = SubmitField('Reset Password')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password',
                                 validators=[DataRequired(), Length(min=10, max=50)])
    new_password = PasswordField('New Password',
                                 validators=[DataRequired(), Length(min=10, max=50)])
    confirm_password = PasswordField('Confirm New Password',
                                     validators=[DataRequired(), EqualTo('new_password')])
    submit_pwd = SubmitField('Update Password')
