from datetime import datetime, timedelta
from time import mktime
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


def get_datetime_from_time_struct(ts):
    if ts:
        return datetime.utcfromtimestamp(mktime(ts))
    return None


def get_24h_from_12h(hour_12, am_or_pm):
    am_or_pm = am_or_pm.lower()
    if hour_12 != 12:
        return hour_12 if am_or_pm == 'am' else (hour_12 + 12)
    else:
        return 0 if am_or_pm == 'am' else 12


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

# Custom date handlers for feedparser


def custom_date_handler(date_string):
    """parse a UTC date in `%A, %B %d, %Y` format"""
    d = datetime.strptime(date_string, "%A, %B %d, %Y")
    return (d.year, d.month, d.day,
            0, 0, 0, 0, 0, 0)
