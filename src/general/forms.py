from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Length, Email


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class HiddenElementForm(FlaskForm):
    hidden_element = StringField('hidden')


class FeedbackForm(FlaskForm):
    name = StringField('Your name*', validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField('Email*',
                        validators=[DataRequired(), Email(message='Not a valid email address')])
    feedback = TextAreaField('Feedback*', validators=[DataRequired(), Length(min=3, max=120)])
    feedback_type = RadioField('Feedback type',
                               choices=[('Bug', 'Bug'), ('Suggestion', 'Suggestion'), ('Other', 'Other')],
                               default='Suggestion')
    submit = SubmitField('Send Feedback')
