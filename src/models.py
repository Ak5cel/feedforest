from flask import url_for
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import smtplib
import ssl
from . import db, login_manager, app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_name = db.Column(db.String(20), unique=True, nullable=False)
    rss_feeds = db.relationship('RSSFeed',
                                backref=db.backref('topic', cascade='all'),
                                lazy=True)
    articles = db.relationship('Article', backref='topic', lazy=True)

    def __repr__(self):
        return f"Topic('{self.topic_name}')"


class RSSFeed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rss_link = db.Column(db.Text, unique=True, nullable=False)
    site_name = db.Column(db.String(30), nullable=False)
    site_url = db.Column(db.Text, unique=True, nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    articles = db.relationship('Article', backref='rssfeed', lazy=True)

    def __repr__(self):
        return f"RSSFeed('{self.rss_link}', '{self.site_name}', '{self.topic.topic_name}')"


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    link = db.Column(db.Text, unique=True, nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    rssfeed_id = db.Column(db.Integer, db.ForeignKey('rss_feed.id'), nullable=False)

    def __repr__(self):
        return f"Article('{self.title}', '{self.link}')"


# Association table between users and followed feeds
user_feed_map = db.Table('user_feed_map',
                         db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                         db.Column('feed_id', db.Integer, db.ForeignKey('rss_feed.id'), primary_key=True))

# Association table between users and bookmarked articles
user_article_map = db.Table('user_article_map',
                            db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                            db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    email_verified = db.Column(db.Boolean, nullable=False, server_default='true')
    selected_feeds = db.relationship('RSSFeed', secondary=user_feed_map, lazy='subquery',
                                     backref=db.backref('selected_by', lazy=True))
    bookmarked_articles = db.relationship('Article', secondary=user_article_map, lazy='subquery',
                                          backref=db.backref('bookmarked_by', lazy=True))

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
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({"user_id": self.id}).decode('utf-8')

    @staticmethod
    def verify_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except Exception:
            return None
        return User.query.get(user_id)

    def generate_token_with_email(self, email, expires_sec=None):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({"user_id": self.id, "email": email}).decode('utf-8')

    @staticmethod
    def verify_token_with_email(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
            email = s.loads(token)['email']
        except Exception:
            return None
        user = User.query.get(user_id)
        return user, email

    @staticmethod
    def send_email(sender_email, receiver_email, message):
        context = ssl.create_default_context()
        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(sender_email, app.config['MAIL_PASSWORD'])
            server.sendmail(sender_email, receiver_email, message)

    def send_password_reset_email(self, token):
        reset_password_link = url_for('reset_password_with_token', token=token, _external=True)
        sender_email = app.config['MAIL_USERNAME']
        receiver_email = self.email
        message = f"""From: FeedForest <{sender_email}>
To: {self.username} <{receiver_email}>
Subject: [FeedForest] Reset Password

Dear {self.username},

Please visit the following link to reset your password:
{reset_password_link}
(The link expires in 30 minutes).

If you have not requested a password reset, simply ignore this message.

Sincerely,
The FeedForest Team
        """
        User.send_email(sender_email, receiver_email, message)

    def send_email_verification_email(self, token):
        verification_link = url_for('verify_email', token=token, _external=True)
        sender_email = app.config['MAIL_USERNAME']
        receiver_email = self.email
        message = f"""From: FeedForest <{sender_email}>
To: {self.username} <{receiver_email}>
Subject: [FeedForest] Verify Email

Dear {self.username},

Please visit the following link to verify your email:
{verification_link}

Sincerely,
The FeedForest Team
        """
        User.send_email(sender_email, receiver_email, message)

    def send_email_change_email(self, token, new_email):
        verification_link = url_for('verify_new_email', token=token, _external=True)
        sender_email = app.config['MAIL_USERNAME']
        receiver_email = new_email
        message = f"""From: FeedForest <{sender_email}>
To: {self.username} <{receiver_email}>
Subject: [FeedForest] Verify Email

Dear {self.username},

Please visit the following link to verify your new email:
{verification_link}

(Your account email will be changed only after verification).

Sincerely,
The FeedForest Team
        """
        User.send_email(sender_email, receiver_email, message)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
