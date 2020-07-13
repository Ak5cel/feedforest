from flask_login import UserMixin
from feedforest import db, login_manager


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
    selected_feeds = db.relationship('RSSFeed', secondary=user_feed_map, lazy='subquery',
                                     backref=db.backref('selected_by', lazy=True))
    bookmarked_articles = db.relationship('Article', secondary=user_article_map, lazy='subquery',
                                          backref=db.backref('bookmarked_by', lazy=True))

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

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
