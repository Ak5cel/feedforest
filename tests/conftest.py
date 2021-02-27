import pytest
from datetime import datetime
# from contextlib import contextmanager
from flask import url_for, template_rendered, current_app
from flask_login import current_user, login_user
from src import create_app, db
from src.models import User, UserRole, Topic, RSSFeed, Article


@pytest.fixture(autouse=True)
def disable_network_emails(monkeypatch):
    def stunted_send_email():
        pass
    monkeypatch.setattr(User, "send_email_verification_email", lambda *args, **kwargs: stunted_send_email())
    monkeypatch.setattr(User, "send_email_change_email", lambda *args, **kwargs: stunted_send_email())
    monkeypatch.setattr(User, "send_password_reset_email", lambda *args, **kwargs: stunted_send_email())


@pytest.fixture()
def client():
    flask_app = create_app()
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    app_ctx = flask_app.app_context()
    app_ctx.push()

    req_ctx = flask_app.test_request_context()
    req_ctx.push()

    yield testing_client

    req_ctx.pop()
    app_ctx.pop()


@pytest.fixture()
def init_database():
    db.create_all()

    # Add user roles now to avoid errors while creating users later
    role1 = UserRole(role_name='admin')
    role2 = UserRole(role_name='user')
    db.session.add_all([role1, role2])
    db.session.commit()
    db.session.execute('pragma foreign_keys=on')
    yield db

    db.drop_all()


@pytest.fixture()
def existing_user():
    """Add a user to the database and return this user"""

    user = User(username="JohnDoe1",
                email="john_doe1@sample.com",
                password_hash=User.hash_password("password123"),
                email_verified=True)
    db.session.add(user)
    db.session.commit()
    yield user


@pytest.fixture()
def logged_in_user(client, existing_user):
    "Returns a logged in user"

    login_user(existing_user)
    yield existing_user


@pytest.fixture()
def existing_topic():
    """Add a topic to the database and return this topic"""

    topic = Topic(topic_name='News')
    db.session.add(topic)
    db.session.commit()
    yield topic


@pytest.fixture()
def existing_feed(existing_topic):
    """Add a feed to the database and return this feed"""

    sample_timestamp = datetime.now()
    feed = RSSFeed(rss_link='test_rss_link',
                   feed_name='test_feed_name',
                   site_url='test_site_url',
                   updated_on=sample_timestamp,
                   topic_id=existing_topic.id)
    db.session.add(feed)
    db.session.commit()
    yield feed


@pytest.fixture()
def existing_article(existing_topic, existing_feed):
    """Add an article to the database and return this article"""

    sample_timestamp = datetime.now()
    article = Article(title='test_title',
                      link='test_link',
                      refreshed_on=sample_timestamp,
                      published_on=sample_timestamp,
                      topic_id=existing_topic.id,
                      rssfeed_id=existing_feed.id)
    db.session.add(article)
    db.session.commit()
    yield article


def generate_topics(n, start_num=0):
    """Generates n topics with consecutive topic names, numbered from `start_num`"""

    for i in range(n):
        yield Topic(topic_name=f"Topic{start_num}")
        start_num += 1


def generate_feeds(feeds_per_topic, topics, start_num=0):
    """Generates specified number of feeds per topic, starting numbering
    at `start_num`
    """

    num_feeds = feeds_per_topic * len(topics)
    for i in range(num_feeds):
        if i % feeds_per_topic == 0:
            topic = topics.pop(0)
        yield RSSFeed(rss_link=f"rss_link_{start_num}",
                      feed_name=f"feed_name_{start_num}",
                      site_url=f"site_url_{start_num}",
                      feed_type="standard",
                      topic=topic)
        start_num += 1


def generate_articles(articles_per_feed, feeds,
                      start_num=0,
                      refreshed_on=datetime.utcnow(),
                      published_on=datetime.utcnow()):
    """Generate specified number of articles per feed, starting numbering
    at `start_num`
    """

    num_articles = articles_per_feed * len(feeds)
    for i in range(num_articles):
        if i % articles_per_feed == 0:
            feed = feeds.pop(0)
        yield Article(title=f"article_title_{start_num}",
                      link=f"link_{start_num}",
                      refreshed_on=refreshed_on,
                      published_on=published_on,
                      rssfeed=feed,
                      topic=feed.topic)
        start_num += 1


@pytest.fixture()
def populate_db_articles():
    """Add 2 topics, 2 RSSFeeds per topic and 3 articles for each feed"""

    topics = list(generate_topics(2))
    feeds = list(generate_feeds(2, topics))

    db.session.add_all(topics)
    db.session.add_all(feeds)
    db.session.add_all([article for article in generate_articles(3, feeds)])
    db.session.commit()
