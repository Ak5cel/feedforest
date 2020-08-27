from itertools import groupby
from operator import attrgetter
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
        image_overlays = {
            "Arts and Entertainment": "https://source.unsplash.com/NYrVisodQ2M",
            "Books": "https://source.unsplash.com/Mmi_sUHNazo",
            "Business": "https://source.unsplash.com/E7RLgUjjazc",
            "Family and Education": "https://source.unsplash.com/4K2lIP0zc_k",
            "Health": "https://source.unsplash.com/eofm5R5f9Kw",
            "Lifestyle": "https://source.unsplash.com/GwNsgnSAfQM",
            "Miscellaneous": "https://source.unsplash.com/IuLgi9PWETU",
            "News": "https://source.unsplash.com/-4phLCSH_4o",
            "Politics": "https://source.unsplash.com/-jqmcOHAQZw",
            "Science and Environment": "https://source.unsplash.com/nyL-rzwP-Mk",
            "Space and Cosmos": "https://source.unsplash.com/6SbFGnQTE8s",
            "Sports": "https://source.unsplash.com/70YxSTWa2Zw",
            "Technology": "https://source.unsplash.com/SYTO3xs06fU",
            "Travel": "https://source.unsplash.com/uSFOwYo1qEw",
            "Web development": "https://source.unsplash.com/gbRaa67fEPo"
        }
    return render_template('index.html',
                           title='Home',
                           topics=topics,
                           image_overlays=image_overlays,
                           articles=articles,
                           last_updated_on=last_updated_on,
                           parse=parse)


@general.route('/topic/<int:id>')
def topic(id):
    topics = Topic.query.all()
    topic = Topic.query.get_or_404(id)
    last_refresh = db.session.query(db.func.max(Article.refreshed_on).label('last_refresh')).scalar()
    latest_articles = db.session.query(Article)\
        .filter_by(topic_id=id, refreshed_on=last_refresh)\
        .order_by(Article.rssfeed_id, Article.published_on.desc())\
        .all()
    articles_grouped = {k: list(g) for k, g in groupby(latest_articles, attrgetter('rssfeed_id'))}
    return render_template('topic.html',
                           topics=topics,
                           topic=topic,
                           articles_grouped=articles_grouped,
                           last_refresh=last_refresh)


@general.route('/about')
def about():
    topics = Topic.query.all()
    return render_template('about.html', title='About Us', topics=topics)


@general.route('/feedback', methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm()
    topics = Topic.query.all()
    if form.validate_on_submit():
        send_feedback_email(name=form.name.data,
                            email=form.email.data,
                            feedback=form.feedback.data,
                            type=form.feedback_type.data)
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('general.feedback'))
    return render_template('feedback.html', title='Feedback', form=form, topics=topics)
