from flask_wtf import FlaskForm
from wtforms import (StringField,
                     SubmitField, RadioField, SelectField)
from wtforms.validators import DataRequired, Length, Email, ValidationError
from flask_login import current_user
from ..models import User


class EditDetailsForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=3, max=30)])
    email = StringField('Email',
                        validators=[DataRequired(), Email(message='Not a valid email address')])
    submit = SubmitField('Update Profile')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user and user.username != current_user.username:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and user.email != current_user.email:
            raise ValidationError('That email is taken. Please choose a different one.')


class EmailPreferencesForm(FlaskForm):
    frequency = RadioField('Email Frequency', choices=[(0, 'Never'), (1, 'Daily')], coerce=int)
    # NOTE: Setting default hour and am_or_pm to prevent validation errors when 'Never' is selected
    hour = SelectField('Hour', choices=[(num, f'{num}:00') for num in range(1, 13)], coerce=int, default=1)
    am_or_pm = SelectField('AM/PM', choices=[('am', 'AM'), ('pm', 'PM')], default='am')
    submit = SubmitField('Update Preferences')
    # Hidden elements
    utc_offset = StringField('offset')
    time_from_db = StringField('time_from_db')
