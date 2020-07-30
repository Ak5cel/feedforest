from datetime import datetime, timedelta
from flask import render_template
from premailer import transform
from . import app
from .models import User


def get_utc_time(hour, offset):
    datetime_obj = datetime(2020, 5, 20, hour, 0, 0, 0)
    offset = timedelta(minutes=offset)
    utc_time = (datetime_obj + offset).time()
    return utc_time


def get_user_locale_time(utc_time, offset):
    datetime_obj = datetime.combine(datetime.today(), utc_time)
    offset = timedelta(minutes=offset)
    user_locale_time = (datetime_obj - offset).time()
    return user_locale_time


def send_feedback_email(name, email, feedback, type):
    User.send_email(
        subject=f'[FeedForest] Feedback: {type}',
        sender_email=app.config['MAIL_USERNAME'],
        receiver_email=app.config['MAIL_USERNAME'],
        text_body=render_template('email/feedback.txt',
                                  name=name,
                                  email=email,
                                  feedback=feedback),
        html_body=transform(render_template('email/feedback-email.html',
                                            name=name,
                                            email=email,
                                            feedback=feedback))
    )
