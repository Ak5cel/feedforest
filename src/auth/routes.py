from flask import render_template, url_for, request, flash, redirect, Blueprint
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse
from ..models import User, Topic
from .forms import (LoginForm, SignupForm,
                    RequestPasswordResetForm, PasswordResetForm)
from .. import db, bcrypt

auth = Blueprint('auth', __name__)


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('user.my_feeds'))
    form = SignupForm()
    topics = Topic.query.all()
    if form.validate_on_submit():
        pw_hash = User.hash_password(form.password.data)
        new_user = User(username=form.username.data,
                        email=form.email.data,
                        password_hash=pw_hash)
        new_user.set_email_verified(False)
        db.session.add(new_user)
        db.session.commit()
        token = new_user.generate_token()
        new_user.send_email_verification_email(token)
        flash('Account created successfully! We have sent you an email to \
            verify your email address.', 'success')
        return render_template('email-verification-sent.html', title='Verify email', topics=topics)
    return render_template('signup.html', title='Sign up', form=form, topics=topics)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.my_feeds'))
    form = LoginForm()
    topics = Topic.query.all()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data) and user.email_verified:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                return redirect(url_for('user.my_feeds'))
            return redirect(next_page)
        else:
            flash('Login unsuccessful. Please check if you are using a \
                verified email and the correct password.', 'danger')
    return render_template('login.html', title='Login', form=form, topics=topics)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('general.home'))


@auth.route('/reset-password', methods=['GET', 'POST'])
def request_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('user.my_feeds'))
    form = RequestPasswordResetForm()
    topics = Topic.query.all()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = user.generate_token(expires_sec=1800)
        user.send_password_reset_email(token)
        flash('Please check your email for a link to reset your password. The link expires in 30 minutes.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('request-password-reset.html', title='Reset Password', form=form, topics=topics)


@auth.route('/reset-password/<string:token>', methods=['GET', 'POST'])
def reset_password_with_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('general.my_feeds'))
    form = PasswordResetForm()
    topics = Topic.query.all()
    if form.validate_on_submit():
        user = User.verify_token(token)
        if user is None:
            flash('Token expired or invalid.', 'warning')
            return redirect(url_for('auth.request_password_reset'))
        pw_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password_hash = pw_hash
        db.session.commit()
        flash('Your password has been reset. You may now login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('password-reset.html', title='Reset Password', form=form, topics=topics)


@auth.route('/verify-email/<string:token>')
def verify_email(token):
    if current_user.is_authenticated:
        flash('Email already verified!.', 'info')
        return redirect(url_for('user.my_feeds'))
    user = User.verify_token(token)
    if user is None:
        flash('Token expired or invalid.', 'warning')
        return render_template('email-verification-sent.html', title='Token expired', topics=Topic.query.all())
    user.email_verified = True
    db.session.commit()
    flash('Email verified. You may now login.', 'success')
    return redirect(url_for('auth.login'))


@auth.route('/verify-new-email/<string:token>')
def verify_new_email(token):
    status = User.verify_token_with_email(token)
    if status is None:
        flash('Invalid Token.', 'warning')
    else:
        user, email = status
        user.email = email
        db.session.commit()
        flash('Email changed! New email: ' + email, 'success')
    return redirect(url_for('user.my_feeds'))
