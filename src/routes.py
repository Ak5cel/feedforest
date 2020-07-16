from flask import render_template, url_for, request, flash, redirect
from flask_login import current_user, login_user, logout_user, login_required
from feedparser import parse
from werkzeug.urls import url_parse
from .models import Topic, RSSFeed, Article, User
from .forms import (LoginForm, SignupForm, EmptyForm,
                    RequestPasswordResetForm, PasswordResetForm,
                    EditDetailsForm, ChangePasswordForm)
from . import app, db, bcrypt


@app.route('/')
@app.route('/home')
def home():
    if request.method == "GET":
        topics = Topic.query.all()
        articles = Article.query.all()
    return render_template('home.html',
                           title='Home',
                           topics=topics,
                           articles=articles,
                           parse=parse)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('my_feeds'))
    form = SignupForm()
    if form.validate_on_submit():
        pw_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data,
                        email=form.email.data,
                        password_hash=pw_hash)
        new_user.set_email_verified(False)
        db.session.add(new_user)
        db.session.commit()
        token = new_user.generate_token()
        new_user.send_email_verification_email(token)
        flash('Account created successfully! We have sent you an email to verify your email address.', 'success')
        return render_template('email-verification-sent.html', title='Verify email')
    return render_template('signup.html', title='Sign up', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('my_feeds'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data) and user.email_verified:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                return redirect(url_for('my_feeds'))
            next_view_name = next_page.split('/')[1]
            return redirect(url_for(next_view_name))
        else:
            flash('Login unsuccessful. Please check if you are using a verified email and the correct password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/myfeeds')
@login_required
def my_feeds():
    return render_template('myfeeds.html', title='My Feeds')


@app.route('/myarticles')
@login_required
def my_articles():
    empty_form = EmptyForm()
    return render_template('myarticles.html', title='My Articles',
                           empty_form=empty_form)


@app.route('/account')
@app.route('/account/summary')
@login_required
def account():
    return render_template('profile-summary.html', title='Account')


@app.route('/account/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    details_form = EditDetailsForm()
    password_form = ChangePasswordForm()
    if details_form.validate_on_submit():
        if details_form.username.data != current_user.username:
            current_user.username = details_form.username.data
            flash('Your username has been updated!', 'success')
        if details_form.email.data != current_user.email:
            token = current_user.generate_token_with_email(details_form.email.data)
            current_user.send_email_change_email(token=token, new_email=details_form.email.data)
            flash("A verification link has been sent to your new email. "
                  "\nYour current email will remain unchanged until the new email "
                  "is verified.", 'info')
            return redirect(url_for('edit_profile'))
    if request.method == 'GET':
        details_form.username.data = current_user.username
        details_form.email.data = current_user.email
    return render_template('edit-profile.html', title='Edit Profile',
                           details_form=details_form, password_form=password_form)


@app.route('/account/edit-feeds', methods=['GET', 'POST'])
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


@app.route('/account/edit-feeds/add', methods=['POST'])
@login_required
def add_feed():
    feed_id = request.args.get('feed_id', type=int)
    current_user.add_feed(feed_id)
    return "Added feed"


@app.route('/account/edit-feeds/remove', methods=['POST'])
@login_required
def remove_feed():
    feed_id = request.args.get('feed_id', type=int)
    current_user.remove_feed(feed_id)
    return "Removed feed"


@app.route('/bookmark', methods=['POST'])
@login_required
def bookmark_article():
    article_id = request.args.get('article_id', type=int)
    current_user.bookmark_article(article_id)
    return "Bookmarked article"


@app.route('/unbookmark', methods=['POST'])
@login_required
def unbookmark_article():
    article_id = request.args.get('article_id', type=int)
    current_user.unbookmark_article(article_id)
    return redirect(url_for('my_articles'))


@app.route('/reset-password', methods=['GET', 'POST'])
def request_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('my_feeds'))
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = user.generate_token(expires_sec=1800)
        user.send_password_reset_email(token)
        flash('Please check your email for a link to reset your password. The link expires in 30 minutes.', 'info')
        return redirect(url_for('login'))
    return render_template('request-password-reset.html', title='Reset Password', form=form)


@app.route('/reset-password/<string:token>', methods=['GET', 'POST'])
def reset_password_with_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('my_feeds'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.verify_token(token)
        if user is None:
            flash('Token expired or invalid.', 'warning')
            return redirect(url_for('request_password_reset'))
        pw_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password_hash = pw_hash
        db.session.commit()
        flash('Your password has been reset. You may now login.', 'success')
        return redirect(url_for('login'))
    return render_template('password-reset.html', title='Reset Password', form=form)


@app.route('/verify-email/<string:token>')
def verify_email(token):
    if current_user.is_authenticated:
        flash('Email already verified!.', 'info')
        return redirect(url_for('my_feeds'))
    user = User.verify_token(token)
    if user is None:
        flash('Invalid Token.', 'warning')
        return redirect(url_for('home'))
    user.email_verified = True
    db.session.commit()
    flash('Email verified. You may now login.', 'success')
    return redirect(url_for('login'))


@app.route('/verify-new-email/<string:token>')
def verify_new_email(token):
    status = User.verify_token_with_email(token)
    if status is None:
        flash('Invalid Token.', 'warning')
    else:
        user, email = status
        user.email = email
        db.session.commit()
        flash('Email changed! New email: ' + email, 'success')
    return redirect(url_for('home'))


@app.route('/account/edit-email-pref')
@login_required
def edit_email_pref():
    return render_template('edit-email-pref.html', title='Account - Edit Feeds')


@app.route('/about')
def about():
    return render_template('about.html', title='About Us')
