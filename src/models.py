from datetime import datetime
from itertools import groupby
from operator import attrgetter
from feedparser import parse
from html import unescape
from flask import url_for, render_template, current_app
from flask_login import UserMixin, current_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy.sql import expression
from sqlalchemy.ext.associationproxy import association_proxy
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
    feed_name = db.Column(db.String(100), nullable=False)
    site_url = db.Column(db.String(2048), nullable=False)
    feed_type = db.Column(db.String(10), default='custom')  # either 'standard' or 'custom'
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
        """
        Returns a dict version of the article where the key is the
        column name/attribute and the value is the corresponding value of
        the attribute.

        Also returns an additional key-value pair to indicate whether
        the article is bookmarked by the current user or not. This is to make it
        easier to render in the Jinja templates based on whether the article is
        bookmarked or not. Only authenticated users can see 'bookmarked' status for
        the article, so "is_bookmarked" is always `False` for anonymous users.

        date_format can be either 'ISO' or 'UTC_STRING'. The datetimes will be formatted
        and returned accordingly. This lets Flask handle the conversion and send the
        values to the templates, without having to use additional html identifiers
        and javascript to perform the conversions.
        """

        result_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}

        if current_user.is_authenticated:
            result_dict["is_bookmarked"] = self in current_user.bookmarked_articles
        else:
            result_dict["is_bookmarked"] = False

        if date_format == 'ISO':
            return result_dict
        elif date_format == 'UTC_STRING':
            result_dict['published_on'] = result_dict['published_on'].strftime('%B %e, %Y, %I:%M %p %Z')
            result_dict['refreshed_on'] = result_dict['refreshed_on'].strftime('%B %e, %Y, %I:%M %p %Z')
            return result_dict

    def __repr__(self):
        return f"Article('{self.title}', '{self.link}')"


# Association table between users and bookmarked articles
user_article_map = db.Table('user_article_map',
                            db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                            db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True),
                            db.Column('bookmarked_on', db.DateTime, default=datetime.utcnow))


class UserFeedAssociation(db.Model):
    """Association object that maps users and followed feeds"""

    __tablename__ = 'user_feed_assoc'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    feed_id = db.Column(db.Integer, db.ForeignKey('rss_feed.id'), primary_key=True)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)
    custom_feed_name = db.Column(db.String(100), default=None)
    custom_topic_id = db.Column(db.Integer, default=None)

    # Bidirectional attribute/collection of "user"/"user_selected_feeds"
    user = db.relationship('User', backref=db.backref('user_selected_feeds',
                                                      cascade='all, delete-orphan'))

    feed = db.relationship('RSSFeed', backref='users')


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
    email_verified = db.Column(db.Boolean, nullable=False, server_default=expression.false())
    email_frequency = db.Column(db.Time)
    assoc_objects = db.relationship('UserFeedAssociation')

    # Association proxy "user_selected_feeds" collection
    # to "feed" attribute
    # Need to specify the association proxy's creator argument to use
    # on append() events
    selected_feeds = association_proxy('user_selected_feeds', 'feed',
                                       creator=lambda feed: UserFeedAssociation(feed=feed))

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

    def add_custom_feed(self, **kwargs):
        # Check whether the feed already exists
        feed = RSSFeed.query.filter_by(rss_link=kwargs.get('rss_link')).first()
        if feed:
            if feed not in self.selected_feeds:
                self.user_selected_feeds.append(UserFeedAssociation(
                    feed=feed,
                    user=self,
                    custom_feed_name=kwargs.get('custom_feed_name'),
                    custom_topic_id=int(kwargs.get('topic'))
                ))
                db.session.commit()
        else:
            # Parse new feed to find more info
            d = parse(kwargs.get('rss_link'))
            # Create a feed record with details from the actual rss feed
            new_feed = RSSFeed(rss_link=kwargs.get('rss_link'),
                               feed_name=d.feed.title,
                               site_url=d.feed.link,
                               feed_type='custom',
                               topic_id=int(kwargs.get('topic')))
            # Add articles to the new feed
            last_refresh = db.session.query(db.func.max(Article.refreshed_on)).scalar()
            for entry in d.entries:
                from .utils import get_datetime_from_time_struct
                published_on = get_datetime_from_time_struct(entry.get('published_parsed'))
                new_article = Article(title=unescape(entry.title),
                                      link=entry.link,
                                      refreshed_on=last_refresh,
                                      published_on=published_on,
                                      topic_id=int(kwargs.get('topic')),
                                      rssfeed=new_feed)
                db.session.add(new_article)
            db.session.add(new_feed)
            # Add new feed to user's selected feeds
            self.user_selected_feeds.append(UserFeedAssociation(
                feed=new_feed,
                user=self,
                custom_feed_name=kwargs.get('custom_feed_name'),
                custom_topic_id=int(kwargs.get('topic'))
            ))

            # Commit all changes
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
        last_refresh = db.session.query(db.func.max(Article.refreshed_on)).scalar()
        articles = db.session.query(Article)\
            .filter_by(refreshed_on=last_refresh, )\
            .order_by(Article.rssfeed_id, Article.published_on.desc())\
            .all()

        # Change the default values of the custom feeds to those specified by the user
        mapping = {obj.feed_id: {'feed_name': obj.custom_feed_name, 'topic_id': obj.custom_topic_id} for obj in self.assoc_objects}
        for article in articles:
            if article.rssfeed.feed_type == 'custom':
                article.rssfeed.feed_name = mapping[article.rssfeed_id]['feed_name']

        # Filter latest articles to only include those from the user's selected feeds
        articles = [article for article in articles if article.rssfeed_id in mapping.keys()]

        # Group the articles by feed
        articles_grouped = {k: list(g) for k, g in groupby(articles, attrgetter('rssfeed_id'))}

        my_feeds_link = url_for('user.my_feeds', _external=True)
        unsubscribe_link = url_for('user.edit_email_pref', _external=True)
        print('Sending email...')
        User.send_email(
            subject="[FeedForest] Here's the latest updates from your feeds",
            sender_email=current_app.config['MAIL_USERNAME'],
            receiver_email=self.email,
            text_body=render_template('email/daily-email.txt',
                                      user=self,
                                      articles=articles,
                                      my_feeds_link=my_feeds_link,
                                      unsubscribe_link=unsubscribe_link),
            html_body=transform(render_template('email/daily-email.html',
                                                user=self,
                                                articles=articles,
                                                articles_grouped=articles_grouped,
                                                my_feeds_link=my_feeds_link,
                                                unsubscribe_link=unsubscribe_link))
        )
        print('Email sent.')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
