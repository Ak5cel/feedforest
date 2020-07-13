from flask import render_template, url_for, request, flash, redirect
from flask_login import current_user, login_user, logout_user, login_required
from feedparser import parse
from werkzeug.urls import url_parse
from feedforest import app
from feedforest.models import Topic, RSSFeed, Article, User
from feedforest.forms import LoginForm, SignupForm, EmptyForm
from feedforest import db, bcrypt


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
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! You may now login.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Sign up', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('my_feeds'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successful.', 'success')
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                return redirect(url_for('my_feeds'))
            next_view_name = next_page.split('/')[1]
            return redirect(url_for(next_view_name))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
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
    return render_template('myarticles.html', title='My Articles')


@app.route('/account')
@app.route('/account/summary')
@login_required
def account():
    return render_template('profile-summary.html', title='Account')


@app.route('/account/edit-profile')
@login_required
def edit_profile():
    return render_template('about.html', title='About Us')


@app.route('/account/edit-feeds', methods=['GET', 'POST'])
@login_required
def edit_feeds():
    topics = Topic.query.all()
    feeds = RSSFeed.query.all()
    empty_form = EmptyForm()
    if empty_form.validate_on_submit():
        result = request.form
        flash(result.get('submit'), 'info')
    return render_template('edit-feeds.html', title='Account - Edit Feeds', topics=topics, feeds=feeds, empty_form=empty_form)


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
    return "Un-bookmarked article"


@app.route('/account/edit-email-pref')
@login_required
def edit_email_pref():
    return render_template('edit-email-pref.html', title='Account - Edit Feeds')


@app.route('/about')
def about():
    return render_template('about.html', title='About Us')
