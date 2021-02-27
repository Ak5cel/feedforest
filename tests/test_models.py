from datetime import datetime
from flask_login import current_user
from src.models import Topic, RSSFeed, Article, UserRole, User


def test_new_topic(client, init_database):
    topic = Topic(topic_name='News')
    assert topic.topic_name == 'News'
    init_database.session.add(topic)
    init_database.session.commit()

    all_topics = Topic.query.all()
    assert len(all_topics) == 1
    newly_added_topic = all_topics[0]
    assert newly_added_topic.id is not None
    assert newly_added_topic.rss_feeds == []
    assert newly_added_topic.articles == []
    assert repr(newly_added_topic) == f"Topic('{newly_added_topic.topic_name}')"


def test_new_rssfeed(client, init_database, existing_topic):
    assert existing_topic.id is not None

    sample_timestamp = datetime.now()
    rssfeed = RSSFeed(rss_link='test_rss_link',
                      feed_name='test_feed_name',
                      site_url='test_site_url',
                      updated_on=sample_timestamp,
                      topic_id=existing_topic.id)

    init_database.session.add(rssfeed)
    init_database.session.commit()

    # Get the newly added feed and check if its attributes were set properly
    newly_added_feed = RSSFeed.query.first()
    assert newly_added_feed.rss_link == 'test_rss_link'
    assert newly_added_feed.feed_name == 'test_feed_name'
    assert newly_added_feed.site_url == 'test_site_url'
    assert newly_added_feed.updated_on == sample_timestamp
    assert newly_added_feed.topic_id == existing_topic.id
    assert repr(newly_added_feed) == (f"RSSFeed('{newly_added_feed.rss_link}', "
                                      f"'{newly_added_feed.feed_name}', "
                                      f"'{newly_added_feed.topic.topic_name}')")

    # Check if its type was assigned as 'custom' by default
    assert newly_added_feed.feed_type == 'custom'

    # Check that the newly added feed has no corresponding articles
    assert newly_added_feed.articles == []

    # Check that id is not None
    assert newly_added_feed.id is not None
    assert newly_added_feed.id == 1


def test_new_article(client, init_database, existing_topic, existing_feed):
    sample_timestamp = datetime.now()
    assert existing_topic.id is not None
    assert existing_feed.id is not None

    article = Article(title='test_title',
                      link='test_link',
                      refreshed_on=sample_timestamp,
                      published_on=sample_timestamp,
                      topic_id=existing_topic.id,
                      rssfeed_id=existing_feed.id)
    init_database.session.add(article)
    init_database.session.commit()

    # Get the newly added article and check if its attributes were set properly
    all_articles = Article.query.all()
    assert len(all_articles) == 1
    newly_added_article = all_articles[0]

    assert newly_added_article.title == 'test_title'
    assert newly_added_article.link == 'test_link'
    assert newly_added_article.refreshed_on == sample_timestamp
    assert newly_added_article.published_on == sample_timestamp
    assert newly_added_article.topic_id == existing_topic.id
    assert newly_added_article.rssfeed_id == existing_feed.id
    assert repr(newly_added_article) == (f"Article('{newly_added_article.title}', "
                                         f"'{newly_added_article.link}')")


def test_article_as_dict_anonymous_and_iso(client, init_database, existing_article):
    res_dict = existing_article.as_dict()
    res_dict2 = existing_article.as_dict(date_format="ISO")
    assert current_user.is_anonymous
    assert res_dict == res_dict2
    assert res_dict == dict(id=existing_article.id,
                            title=existing_article.title,
                            link=existing_article.link,
                            refreshed_on=existing_article.refreshed_on,
                            published_on=existing_article.published_on,
                            topic_id=existing_article.topic_id,
                            rssfeed_id=existing_article.rssfeed_id,
                            is_bookmarked=False)


def test_article_as_dict_anonymous_and_utc(client, init_database, existing_article):
    res_dict = existing_article.as_dict(date_format="UTC_STRING")
    assert current_user.is_anonymous
    UTC_FORMAT_STRING = '%B %e, %Y, %I:%M %p %Z'

    def utc_from_datetime(dt):
        return dt.strftime(UTC_FORMAT_STRING)

    utc_formatted_refreshed_on = utc_from_datetime(existing_article.refreshed_on)
    utc_formatted_published_on = utc_from_datetime(existing_article.published_on)
    assert res_dict == dict(id=existing_article.id,
                            title=existing_article.title,
                            link=existing_article.link,
                            refreshed_on=utc_formatted_refreshed_on,
                            published_on=utc_formatted_published_on,
                            topic_id=existing_article.topic_id,
                            rssfeed_id=existing_article.rssfeed_id,
                            is_bookmarked=False)


def test_article_as_dict_bookmarked(client, init_database,
                                    logged_in_user, existing_article):
    assert current_user.is_authenticated
    assert logged_in_user.is_authenticated
    assert current_user == logged_in_user

    # Add the existing article to the current_user's list of bookmarked articles
    logged_in_user.bookmarked_articles.append(existing_article)
    init_database.session.commit()

    res_dict = existing_article.as_dict()
    assert res_dict == dict(id=existing_article.id,
                            title=existing_article.title,
                            link=existing_article.link,
                            refreshed_on=existing_article.refreshed_on,
                            published_on=existing_article.published_on,
                            topic_id=existing_article.topic_id,
                            rssfeed_id=existing_article.rssfeed_id,
                            is_bookmarked=True)


def test_new_user(client, init_database):
    user = User(username="test_username",
                email="test_email",
                password_hash=User.hash_password("test_password"))
    init_database.session.add(user)
    init_database.session.commit()

    # Get the newly added user and check if its attributes were set properly
    all_users = User.query.all()
    assert len(all_users) == 1
    newly_added_user = all_users[0]

    assert newly_added_user.id is not None
    assert newly_added_user.username == 'test_username'
    assert newly_added_user.email == 'test_email'
    assert newly_added_user.password_hash is not None
    assert newly_added_user.password_hash != "test_password"
    assert not newly_added_user.email_verified
    assert newly_added_user.assoc_objects == []
    assert newly_added_user.selected_feeds == []
    assert newly_added_user.bookmarked_articles == []
    assert newly_added_user.role_id == UserRole.get_default_role_id()
    assert repr(newly_added_user) == (f"User('{newly_added_user.username}', "
                                      f"'{newly_added_user.email}')")


def test_user_check_password_against_hash():
    user = User(username="test_username",
                email="test_email",
                password_hash=User.hash_password("correct_password"))
    assert user.check_password("correct_password")
    assert not user.check_password("incorrect_password")


def test_user_hash_password():
    pwd1 = 'password_1'
    pwd2 = 'password_2'
    pwd1_copy = 'password_1'
    pwd1_hash = User.hash_password(pwd1)
    pwd2_hash = User.hash_password(pwd2)
    pwd1_copy_hash = User.hash_password(pwd1_copy)

    assert pwd1 != pwd1_hash
    assert pwd2 != pwd2_hash
    assert pwd1_copy != pwd1_copy_hash
    assert pwd1_hash != pwd2_hash

    # Check that two identical passwords are not hashed to the same value
    assert pwd1_hash != pwd1_copy_hash


def test_user_set_email_verified():
    user = User(username="test_username",
                email="test_email",
                password_hash=User.hash_password("test_password"),
                email_verified=False)
    assert not user.email_verified

    user.set_email_verified(True)
    assert user.email_verified
    user.set_email_verified(False)
    assert not user.email_verified


# TODO: Add more exhaustive tests for add_feed, possibly will need to add exception
# handing when feed_id is not an int, or there doesn't exist a feed with that
# feed_id, etc.
def test_user_add_feed(client, init_database, existing_feed, existing_user):
    assert len(existing_user.selected_feeds) == 0

    existing_user.add_feed(existing_feed.id)
    assert len(existing_user.selected_feeds) == 1
    assert existing_user.selected_feeds[0] == existing_feed


def test_user_try_adding_already_subscribed_feed(client, init_database,
                                                 existing_feed, existing_user):
    # Subscribe to the existing feed first
    assert len(existing_user.selected_feeds) == 0
    existing_user.selected_feeds.append(existing_feed)
    init_database.session.commit()
    assert len(existing_user.selected_feeds) == 1
    assert existing_user.selected_feeds[0] == existing_feed

    # Try subscibing to the same feed again, it should not be added twice
    existing_user.add_feed(existing_feed.id)
    assert len(existing_user.selected_feeds) == 1
    assert existing_user.selected_feeds[0] == existing_feed
