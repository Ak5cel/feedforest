from datetime import datetime
from flask import url_for, render_template, current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy.sql import expression
from premailer import transform
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from . import db, login_manager, bcrypt


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_name = db.Column(db.String(30), index=True, unique=True, nullable=False)
    rss_feeds = db.relationship('RSSFeed',
                                backref=db.backref('topic', cascade='all'),
                                lazy=True)
    articles = db.relationship('Article',
                               backref='topic',
                               order_by="asc(Article.rssfeed_id)",
                               lazy=True)

    def __repr__(self):
        return f"Topic('{self.topic_name}')"


class RSSFeed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rss_link = db.Column(db.String(768), unique=True, nullable=False)
    feed_name = db.Column(db.String(100), index=True, unique=True, nullable=False)
    site_url = db.Column(db.String(2048), nullable=False)
    updated_on = db.Column(db.DateTime)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    articles = db.relationship('Article', backref='rssfeed', lazy=True)

    def __repr__(self):
        return f"RSSFeed('{self.rss_link}', '{self.feed_name}', '{self.topic.topic_name}')"


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(2048), nullable=False)
    refreshed_on = db.Column(db.DateTime)
    published_on = db.Column(db.DateTime)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    rssfeed_id = db.Column(db.Integer, db.ForeignKey('rss_feed.id'), nullable=False)

    def as_dict(self, date_format="ISO"):
        result_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if date_format == 'ISO':
            return result_dict
        elif date_format == 'UTC_STRING':
            result_dict['published_on'] = result_dict['published_on'].strftime('%B %e, %Y, %I:%M %p %Z')
            result_dict['refreshed_on'] = result_dict['refreshed_on'].strftime('%B %e, %Y, %I:%M %p %Z')
            return result_dict

    def __repr__(self):
        return f"Article('{self.title}', '{self.link}')"


# Association table between users and followed feeds
user_feed_map = db.Table('user_feed_map',
                         db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                         db.Column('feed_id', db.Integer, db.ForeignKey('rss_feed.id'), primary_key=True),
                         db.Column('added_on', db.DateTime, default=datetime.utcnow))

# Association table between users and bookmarked articles
user_article_map = db.Table('user_article_map',
                            db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                            db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True),
                            db.Column('bookmarked_on', db.DateTime, default=datetime.utcnow))


class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(20))

    users = db.relationship('User',
                            backref=db.backref('role', lazy=True),
                            passive_deletes="all")

    @staticmethod
    def get_default_role_id():
        DEFAULT_ROLE_NAME = 'user'
        return UserRole.get_role(DEFAULT_ROLE_NAME).id

    @staticmethod
    def get_role(role_name):
        return UserRole.query.filter_by(role_name=role_name).first()

    def __repr__(self):
        return f"UserRole('{self.id}', '{self.role_name}')"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), index=True, unique=True, nullable=False)
    email = db.Column(db.String(254), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    email_verified = db.Column(db.Boolean, nullable=False, server_default=expression.true())
    email_frequency = db.Column(db.Time)
    selected_feeds = db.relationship('RSSFeed', secondary=user_feed_map, lazy='subquery',
                                     backref=db.backref('selected_by', lazy=True))
    bookmarked_articles = db.relationship('Article', secondary=user_article_map, lazy='subquery',
                                          backref=db.backref('bookmarked_by', lazy=True))
    role_id = db.Column(db.Integer,
                        db.ForeignKey('user_role.id',
                                      onupdate="CASCADE",
                                      ondelete="SET DEFAULT"),
                        default=UserRole.get_default_role_id)

    def check_password(self, pw):
        return bcrypt.check_password_hash(self.password_hash, pw)

    @staticmethod
    def hash_password(pw):
        return bcrypt.generate_password_hash(pw).decode('utf-8')

    def set_email_verified(self, bool):
        self.email_verified = bool

    def add_feed(self, feed_id):
        if int(feed_id):
            feed = RSSFeed.query.get(int(feed_id))
            if feed not in self.selected_feeds:
                self.selected_feeds.append(feed)
                db.session.commit()

    def remove_feed(self, feed_id):
        if int(feed_id):
            feed = RSSFeed.query.get(int(feed_id))
            if feed in self.selected_feeds:
                self.selected_feeds.remove(feed)
                db.session.commit()

    def bookmark_article(self, article_id):
        if int(article_id):
            article = Article.query.get(int(article_id))
            if article not in self.bookmarked_articles:
                self.bookmarked_articles.append(article)
                db.session.commit()

    def unbookmark_article(self, article_id):
        if int(article_id):
            article = Article.query.get(int(article_id))
            if article in self.bookmarked_articles:
                self.bookmarked_articles.remove(article)
                db.session.commit()

    def generate_token(self, expires_sec=None):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({"user_id": self.id}).decode('utf-8')

    @staticmethod
    def verify_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except Exception:
            return None
        return User.query.get(user_id)

    def generate_token_with_email(self, email, expires_sec=None):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({"user_id": self.id, "email": email}).decode('utf-8')

    @staticmethod
    def verify_token_with_email(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
            email = s.loads(token)['email']
        except Exception:
            return None
        user = User.query.get(user_id)
        return user, email

    @staticmethod
    def send_email(subject,
                   sender_email,
                   receiver_email,
                   text_body,
                   html_body):
        # MIMEMultipart setup
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = receiver_email

        # Create text and hml MIMEText objects
        part1 = MIMEText(text_body, "plain")
        part2 = MIMEText(html_body, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(sender_email, current_app.config['MAIL_PASSWORD'])
            server.sendmail(sender_email, receiver_email, message.as_string())

    def send_password_reset_email(self, token):
        reset_password_link = url_for('auth.reset_password_with_token', token=token, _external=True)
        sender_email = current_app.config['MAIL_USERNAME']
        receiver_email = self.email
        User.send_email(
            subject='[FeedForest] Reset Password',
            sender_email=sender_email,
            receiver_email=receiver_email,
            text_body=render_template('email/reset-password.txt',
                                      user=self,
                                      reset_password_link=reset_password_link),
            html_body=transform(render_template('email/reset-password.html',
                                                user=self,
                                                reset_password_link=reset_password_link))
        )

    def send_email_verification_email(self, token):
        verification_link = url_for('auth.verify_email', token=token, _external=True)
        sender_email = current_app.config['MAIL_USERNAME']
        receiver_email = self.email
        User.send_email(
            subject='[FeedForest] Verify Email',
            sender_email=sender_email,
            receiver_email=receiver_email,
            text_body=render_template('email/verify-email.txt',
                                      user=self,
                                      verification_link=verification_link),
            html_body=transform(render_template('email/verify-email.html',
                                                user=self,
                                                verification_link=verification_link))
        )

    def send_email_change_email(self, token, new_email):
        verification_link = url_for('auth.verify_new_email', token=token, _external=True)
        sender_email = current_app.config['MAIL_USERNAME']
        receiver_email = new_email
        User.send_email(
            subject='[FeedForest] Verify New Email',
            sender_email=sender_email,
            receiver_email=receiver_email,
            text_body=render_template('email/change-email.txt',
                                      user=self,
                                      verification_link=verification_link),
            html_body=transform(render_template('email/change-email.html',
                                                user=self,
                                                verification_link=verification_link,
                                                new_email=new_email)
                                )
        )

    def send_daily_email(self):
        print('Entered method')
        sub = db.session.query(db.func.max(Article.refreshed_on).label('last_refresh')).subquery()
        latest_articles = db.session.query(Article).join(sub, sub.c.last_refresh == Article.refreshed_on).all()
        my_feeds_link = url_for('user.my_feeds', _external=True)
        unsubscribe_link = url_for('user.edit_email_pref', _external=True)
        print('Sending email...')
        User.send_email(
            subject="[FeedForest] Here's the latest updates from your feeds",
            sender_email=current_app.config['MAIL_USERNAME'],
            receiver_email=self.email,
            text_body=render_template('email/daily-email.txt',
                                      user=self,
                                      articles=latest_articles,
                                      my_feeds_link=my_feeds_link,
                                      unsubscribe_link=unsubscribe_link),
            html_body=transform(render_template('email/daily-email.html',
                                                user=self,
                                                articles=latest_articles,
                                                my_feeds_link=my_feeds_link,
                                                unsubscribe_link=unsubscribe_link))
        )
        print('Email sent.')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
