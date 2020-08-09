from flask import render_template, url_for, request, flash, redirect, Blueprint
from feedparser import parse
from ..models import Topic, Article
from .forms import FeedbackForm
from .. import db
from ..utils import send_feedback_email

general = Blueprint('general', __name__)


@general.route('/')
@general.route('/home')
def home():
    if request.method == "GET":
        topics = Topic.query.all()
        sub = db.session.query(db.func.max(Article.refreshed_on).label('last_refresh')).subquery()
        articles = db.session.query(Article).join(sub, sub.c.last_refresh == Article.refreshed_on).all()
        last_updated_on = db.session.query(db.func.max(Article.refreshed_on)).scalar()
    return render_template('home.html',
                           title='Home',
                           topics=topics,
                           articles=articles,
                           last_updated_on=last_updated_on,
                           parse=parse)


@general.route('/about')
def about():
    return render_template('about.html', title='About Us')


@general.route('/feedback', methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        send_feedback_email(name=form.name.data,
                            email=form.email.data,
                            feedback=form.feedback.data,
                            type=form.feedback_type.data)
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('general.feedback'))
    return render_template('feedback.html', title='Feedback', form=form)
