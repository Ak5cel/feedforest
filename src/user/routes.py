from flask import render_template, url_for, request, flash, redirect, Blueprint
from flask_login import current_user, login_required
from ..models import Topic, RSSFeed, Article, User, user_article_map
from ..general.forms import EmptyForm, HiddenElementForm
from ..auth.forms import ChangePasswordForm
from .forms import EditDetailsForm, EmailPreferencesForm
from .. import db
from ..utils import get_utc_time, get_24h_from_12h

user = Blueprint('user', __name__)


@user.route('/feeds')
@login_required
def my_feeds():
    sub = db.session.query(db.func.max(Article.refreshed_on).label('last_refresh')).subquery()
    latest_articles = db.session.query(Article).join(sub, sub.c.last_refresh == Article.refreshed_on).all()
    last_updated_on = db.session.query(db.func.max(Article.refreshed_on)).scalar()
    return render_template('myfeeds.html',
                           title='My Feeds',
                           latest_articles=latest_articles,
                           last_updated_on=last_updated_on)


@user.route('/articles')
@login_required
def my_articles():
    empty_form = EmptyForm()
    bookmarked_articles = Article.query\
        .join(user_article_map, (Article.id == user_article_map.c.article_id))\
        .filter(user_article_map.c.user_id == current_user.id)\
        .order_by(user_article_map.c.bookmarked_on.desc())\
        .all()
    return render_template('myarticles.html', title='My Articles',
                           empty_form=empty_form, bookmarked_articles=bookmarked_articles)


@user.route('/account')
@user.route('/account/summary')
@login_required
def account():
    hidden_time_form = HiddenElementForm()
    hidden_time_form.hidden_element.data = current_user.email_frequency
    return render_template('profile-summary.html', title='Account', hidden_time_form=hidden_time_form)


@user.route('/account/edit/feeds', methods=['GET', 'POST'])
@login_required
def edit_feeds():
    topics = Topic.query.all()
    feeds = RSSFeed.query.all()
    empty_form = EmptyForm()
    if empty_form.validate_on_submit():
        result = request.form
        flash(result.get('submit'), 'info')
    return render_template('edit-feeds.html', title='Account - Edit Feeds',
                           topics=topics, feeds=feeds, empty_form=empty_form)


@user.route('/account/edit/feeds/add', methods=['POST'])
@login_required
def add_feed():
    feed_id = request.args.get('feed_id', type=int)
    current_user.add_feed(feed_id)
    return "Added feed"


@user.route('/account/edit/feeds/remove', methods=['POST'])
@login_required
def remove_feed():
    feed_id = request.args.get('feed_id', type=int)
    current_user.remove_feed(feed_id)
    return "Removed feed"


@user.route('/bookmark', methods=['POST'])
@login_required
def bookmark_article():
    article_id = request.args.get('article_id', type=int)
    current_user.bookmark_article(article_id)
    return "Bookmarked article"


@user.route('/unbookmark', methods=['POST'])
@login_required
def unbookmark_article():
    article_id = request.args.get('article_id', type=int)
    current_user.unbookmark_article(article_id)
    return redirect(url_for('user.my_articles'))


@user.route('/account/edit/email-pref', methods=['GET', 'POST'])
@login_required
def edit_email_pref():
    form = EmailPreferencesForm()
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
    return render_template('edit-email-pref.html', title='Account - Email Preferences', form=form)


@user.route('/account/edit/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    details_form = EditDetailsForm()
    password_form = ChangePasswordForm()
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
                           details_form=details_form, password_form=password_form)
