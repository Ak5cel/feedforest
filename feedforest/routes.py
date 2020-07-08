from flask import render_template, url_for, request, flash, redirect
from flask_login import current_user, login_user, logout_user, login_required
from feedparser import parse
from werkzeug.urls import url_parse
from feedforest import app
from feedforest.models import Topic, Article, User
from feedforest.forms import LoginForm, SignupForm
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
            return redirect(url_for(next_page))
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
    return render_template('about.html', title='About Us')


@app.route('/account')
@login_required
def account():
    return render_template('account.html', title='About Us')


@app.route('/about')
def about():
    return render_template('about.html', title='About Us')
