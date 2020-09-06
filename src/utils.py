from datetime import datetime, timedelta
from time import mktime
import urllib
from feedparser import parse
from flask import render_template, current_app
from premailer import transform
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


def check_broken_link(url):
    """Check whether the url is broken.
    Return tuple (result, status_code, reason) after the check.

    If the url is broken, return (True, status_code, reason).
        If urllib.error.HTTPError is raised, status_code and reason are not None
        If urllib.error.URLError is raised, status_code is None
        In case of all other Exceptions, status_code is None and reason
        is 'Unexpected Error'
    If the url is not broken, result is False and reason is None
    """

    try:
        res = urllib.request.urlopen(url)
        return (False, res.getcode(), None)
    except urllib.error.HTTPError as e:
        return (True, e.code, e.reason)
    except urllib.error.URLError as e:
        return (True, None, e.reason)
    except Exception as e:
        return (True, None, e)


def check_valid_feed(url):
    """Check whether the feed at the URL is well-formed and whether
    it has been permanently redirected, marked as 'gone', or invalid in
    any other way.

    Returns (result, message)
    result is True for a valid feed and False otherwise
    message is None for a valid feed, the appropriate message is
    returned otherwise.
    """
    d = parse(url)
    if 'status' in d.keys():
        if d.status == 301:
            result = False
            message = f'301: The feed has been permanently redirected to {d.href}. \
            Please use the new URL instead.'
        elif d.status == 410:
            result = False
            message = f"The feed is marked as 'Gone' and is no longer available\
             at the origin server. This condition is likely to be permanent."
        elif d.status > 299:
            result, status_code, reason = check_broken_link(url)
            message = f'Error {status_code if status_code else ""}: {reason}'
        elif d.bozo:
            result = False
            if 'text/html' in d.headers['Content-Type']:
                message = "The target feed has a Content-Type of text/html and \
                is not a valid xml feed"
            else:
                message = "The target feed is not a well-formed xml page."
        else:
            result = True
            message = None
    else:
        result, status_code, reason = check_broken_link(url)
        result = not result  # Reversed becaus check_broken_link returns True for broken links
        message = f'Error {status_code if status_code else ""}: {reason}'

    return (result, message)


def send_feedback_email(name, email, feedback, type):
    User.send_email(
        subject=f'[FeedForest] Feedback: {type}',
        sender_email=current_app.config['MAIL_USERNAME'],
        receiver_email=current_app.config['MAIL_USERNAME'],
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
