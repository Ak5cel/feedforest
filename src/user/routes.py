from itertools import groupby
from operator import attrgetter
import json
from flask import render_template, url_for, request, flash, redirect, Blueprint, jsonify, make_response
from flask_login import current_user, login_required
from ..models import Topic, RSSFeed, Article, User, user_article_map, UserFeedAssociation
from ..general.forms import EmptyForm, HiddenElementForm
from ..auth.forms import ChangePasswordForm
from .forms import EditDetailsForm, EmailPreferencesForm, AddCustomFeedForm
from .. import db
from ..utils import get_utc_time, get_24h_from_12h

user = Blueprint('user', __name__)


@user.route('/user/feeds')
@login_required
def my_feeds():
    last_refresh = db.session.query(db.func.max(Article.refreshed_on)).scalar()
    latest_articles = db.session.query(Article)\
        .filter_by(refreshed_on=last_refresh)\
        .order_by(Article.rssfeed_id, Article.published_on.desc())\
        .all()
    articles_grouped = {k: list(g) for k, g in groupby(latest_articles, attrgetter('rssfeed_id'))}
    topics = Topic.query.all()
    return render_template('myfeeds.html',
                           title='My Feeds',
                           articles_grouped=articles_grouped,
                           last_updated_on=last_refresh,
                           topics=topics)


@user.route('/user/articles')
@login_required
def my_articles():
    empty_form = EmptyForm()
    bookmarked_articles = Article.query\
        .join(user_article_map, (Article.id == user_article_map.c.article_id))\
        .filter(user_article_map.c.user_id == current_user.id)\
        .order_by(user_article_map.c.bookmarked_on.desc())\
        .all()
    topics = Topic.query.all()
    return render_template('myarticles.html',
                           title='My Articles',
                           empty_form=empty_form,
                           bookmarked_articles=bookmarked_articles,
                           topics=topics)


@user.route('/user/inbox/all')
def inbox():
    articles = db.session.query(Article).join(UserFeedAssociation, (Article.rssfeed_id == UserFeedAssociation.feed_id))\
        .filter(UserFeedAssociation.user_id == current_user.id, db.func.DATE(Article.refreshed_on) >= db.func.DATE(UserFeedAssociation.added_on))\
        .order_by(Article.rssfeed_id, Article.published_on.desc())\
        .all()
    articles_grouped = {k: list(g) for k, g in groupby(articles, attrgetter('rssfeed_id'))}
    topics = Topic.query.all()
    return render_template('inbox-all.html',
                           title='Inbox',
                           articles_grouped=articles_grouped,
                           topics=topics)


@user.route('/user/inbox/')
def inbox_for_topic():
    feed_id = request.args.get('feed_id')
    selected_feed = RSSFeed.query.get_or_404(feed_id)
    if selected_feed not in current_user.selected_feeds:
        flash(f"You have not subscribed to that feed.", 'warning')
        return redirect(url_for('user.inbox'))
    added_on = db.session.query(UserFeedAssociation.added_on)\
        .filter(UserFeedAssociation.user_id == current_user.id, UserFeedAssociation.feed_id == selected_feed.id)\
        .scalar()
    articles = Article.query.filter(db.func.DATE(Article.refreshed_on) >= db.func.DATE(added_on), Article.rssfeed_id == selected_feed.id).distinct().all()
    topics = Topic.query.all()
    return render_template('inbox-topic.html',
                           title='Inbox',
                           articles=articles,
                           selected_feed=selected_feed,
                           topics=topics,
                           str=str)


@user.route('/account')
@user.route('/account/summary')
@login_required
def account():
    hidden_time_form = HiddenElementForm()
    hidden_time_form.hidden_element.data = current_user.email_frequency
    topics = Topic.query.all()
    return render_template('profile-summary.html', title='Account', hidden_time_form=hidden_time_form, topics=topics)


@user.route('/account/edit/feeds', methods=['GET', 'POST'])
@login_required
def edit_feeds():
    topics = Topic.query.order_by(Topic.id).all()

    # Feeds are ordered by feed type to group them later
    feeds = RSSFeed.query.order_by(RSSFeed.feed_type, RSSFeed.topic_id).all()

    # Group the feeds into 2 types based on feed type - custom and standard
    feeds_grouped = {feed_type: list(feeds) for feed_type, feeds in groupby(feeds, attrgetter('feed_type'))}

    # Filter custom feeds to only include those added by the current user
    feeds_grouped['custom'] = [feed for feed in feeds_grouped.get('custom', []) if feed in current_user.selected_feeds]

    # Change the default values of the custom feeds to those specified by the user
    mapping = {obj.feed_id: {'feed_name': obj.custom_feed_name, 'topic_id': obj.custom_topic_id} for obj in current_user.assoc_objects}
    if feeds_grouped.get('custom'):
        for feed in feeds_grouped['custom']:
            feed.feed_name = mapping[feed.id]['feed_name']
            feed.topic_id = mapping[feed.id]['topic_id']
            feed.topic = list(topic for topic in topics if topic.id == feed.topic_id)[0]

    empty_form = EmptyForm()
    add_feed_form = AddCustomFeedForm()
    add_feed_form.topic.choices = [(t.id, t.topic_name) for t in topics]
    if add_feed_form.validate_on_submit():
        form_data = {field.name: field.data for field in add_feed_form}
        current_user.add_custom_feed(**form_data)
        return make_response(jsonify({"data": 'ok', "message": "ok"}), 200)
    elif request.method == 'POST' and not add_feed_form.validate():
        return make_response(jsonify({"data": add_feed_form.errors, "message": "error"}))
    return render_template('edit-feeds.html', title='Account - Edit Feeds',
                           topics=topics, feeds_grouped=feeds_grouped, empty_form=empty_form,
                           add_feed_form=add_feed_form)


@user.route('/account/edit/feeds/add', methods=['POST'])
@login_required
def add_feed():
    feed_id = request.args.get('feed_id', type=int)
    current_user.add_feed(feed_id)
    return "Added feed"


@user.route('/account/edit/feeds/add-custom', methods=['POST'])
@login_required
def add_custom_feed():
    custom_feed_name = request.args.get('custom_feed_name')
    rss_link = request.args.get('rss_link')
    topic = request.args.get('topic')
    return redirect(url_for('user.edit_feeds'))


@user.route('/account/edit/feeds/remove', methods=['POST'])
@login_required
def remove_feed():
    feed_id = request.args.get('feed_id', type=int)
    current_user.remove_feed(feed_id)
    return "Removed feed"


@user.route('/bookmark', methods=['GET', 'POST'])
def bookmark_article():
    if not current_user.is_authenticated:
        res = make_response(jsonify({"message": "LOGIN_REQUIRED", "redirect": url_for('auth.login', next=request.full_path, _external=True)}), 401)
        flash('Login to bookmark articles, and more!', 'info')
        return res
    article_id = request.args.get('article_id', type=int)
    current_user.bookmark_article(article_id)
    if request.method == 'GET':
        article = Article.query.get(article_id)
        return redirect(url_for('general.topic', id=article.topic_id))
    res = make_response(jsonify({"message": f"Bookmarked article {article_id}"}), 200)
    return res


@user.route('/unbookmark', methods=['POST'])
@login_required
def unbookmark_article():
    if not current_user.is_authenticated:
        res = make_response(jsonify({"message": "LOGIN_REQUIRED", "redirect": url_for('auth.login', next=request.full_path, _external=True)}), 401)
        return res
    article_id = request.args.get('article_id', type=int)
    current_user.unbookmark_article(article_id)
    res = make_response(jsonify({"message": f"Unbookmarked article {article_id}"}), 200)
    return res


@user.route('/account/edit/email-pref', methods=['GET', 'POST'])
@login_required
def edit_email_pref():
    form = EmailPreferencesForm()
    topics = Topic.query.all()
    if form.validate_on_submit():
        if form.frequency.data == 0:
            current_user.email_frequency = None
        elif form.frequency.data == 1:
            hour_24 = get_24h_from_12h(form.hour.data, form.am_or_pm.data)
            utc_offset = int(form.utc_offset.data)
            time_utc = get_utc_time(hour_24, utc_offset)
            current_user.email_frequency = time_utc
        db.session.commit()
        flash('Your preferences have been updated!', 'success')
        return redirect(url_for('user.edit_email_pref'))
    else:
        form.frequency.data = 1 if current_user.email_frequency else 0
        form.time_from_db.data = current_user.email_frequency
    return render_template('edit-email-pref.html', title='Account - Email Preferences', form=form, topics=topics)


@user.route('/account/edit/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    details_form = EditDetailsForm()
    password_form = ChangePasswordForm()
    topics = Topic.query.all()
    if details_form.submit.data and details_form.validate():
        if details_form.username.data != current_user.username:
            current_user.username = details_form.username.data
            db.session.commit()
            flash('Your username has been updated!', 'success')
        if details_form.email.data != current_user.email:
            token = current_user.generate_token_with_email(details_form.email.data)
            current_user.send_email_change_email(token=token, new_email=details_form.email.data)
            flash("A verification link has been sent to your new email. "
                  "\nYour current email will remain unchanged until the new email "
                  "is verified.", 'info')
            return redirect(url_for('user.edit_profile'))
    elif password_form.submit_pwd.data and password_form.validate():
        if not current_user.check_password(password_form.old_password.data):
            flash('Old password incorrect.', 'danger')
        else:
            current_user.password_hash = User.hash_password(password_form.new_password.data)
            db.session.commit()
            flash('Password updated!', 'success')
        return redirect(url_for('user.edit_profile'))
    else:
        details_form.username.data = current_user.username
        details_form.email.data = current_user.email
    return render_template('edit-profile.html', title='Edit Profile',
                           details_form=details_form, password_form=password_form, topics=topics)
