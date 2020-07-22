from datetime import datetime
from time import mktime
from feedparser import parse
from . import celery, db, app
from .models import RSSFeed, Article
from celery.schedules import crontab

# Logging setup for debugging
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
# Comment this out to enable logging mode
# logging.disable(logging.CRITICAL)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # FOR TESTING ONLY
    # Remove before deployment
    sender.add_periodic_task(10.0, greet.s('Akhila'))
    
    # Calls fetch_articles() every hour    
    sender.add_periodic_task(
        crontab(minute='*/5'),
        fetch_articles.s()
        )

@celery.task
def greet(name):
    print('Hello' + name)


@celery.task
def fetch_articles():
    
    # -----------------------------------------------------------------
    # THE PROCESS:
    #   * When the script is started, set CURRENT_REFRESH_TIME as utcnow()
    # 1. Clear all articles except user saved articles
    # 2. Go through each RSSFeed, check whether the updated_on column
    #    matches the updated field
    # 3.a. If it does not, get the new batch of articles.
    #      For each article, check whether it is aleady in the table.
    #      If it is, change its refreshed_on.
    #      If it is not, add it.
    #   b. If it does, get the articles with the latest refresh time.
    #      Change their refreshed_on to the new value.
    # -----------------------------------------------------------------
    
    # Sets number of articles to extract from each feed
    MAX_ARTICLES_COUNT = 3

    # When the script is started, set CURRENT_REFRESH_TIME
    CURRENT_REFRESH_TIME = datetime.utcnow()

    # First, clear all articles except user saved articles.
    # This is so that only the most recent records exist in the table
    Article.query.filter(~Article.bookmarked_by.any()).delete(synchronize_session=False)
    logging.debug('Cleared unbookmarked articles')

    # Fetch a list of all RSS feeds from the db
    rssfeeds = RSSFeed.query.all()
    logging.debug(f'Fetched {len(rssfeeds)} RSS Feeds')

    for feed in rssfeeds:
        # Parse the feed
        logging.debug(f'Parsing feed: {feed}...')
        parsed_feed = parse(feed.rss_link)

        # Get the time the feed was last updated
        ts = parsed_feed.feed.get('updated_parsed', None)  # returns a time.struct_time instance
        if ts:
            updated_on = datetime.utcfromtimestamp(mktime(ts))  # converts time.struct_time into UTC datetime.datetime instance

        # Check whether the feed was updated since last database refresh
        if ts and feed.updated_on == updated_on:
            logging.debug('Feed up-to-date. Updating refresh times to current time...')
            # If the feed is up-to-date, get the articles from that feed
            # from the previous refresh.
            # Change their refreshed_on to the new value.
            previous_refresh = db.session.query(db.func.max(Article.refreshed_on)).scalar()
            status = Article.query\
                .filter_by(rssfeed=feed, refreshed_on=previous_refresh)\
                .update({Article.refreshed_on: CURRENT_REFRESH_TIME}, synchronize_session='evaluate')
            if status == 0:
                logging.debug('Update FAILED')
                db.session.rollback()
            elif status > 0:
                logging.debug('Update successful')
        else:
            logging.debug('Remote Feed has been updated. Fetching latest articles...')
            # Extract the first 3 articles from the parsed feed
            entries = parsed_feed.entries[:MAX_ARTICLES_COUNT]
            logging.debug(f'Fetched {len(entries)} articles.')

            for entry in entries:
                logging.debug(f'Checking Article {entries.index(entry)}')
                # For each article, check whether it is aleady in the table.
                # If it is, change its refreshed_on.
                # Otherwise, add it to the table.
                duplicate_article = Article.query.filter_by(link=entry.link).first()
                if duplicate_article:
                    logging.debug(f'Duplicate Article ({entries.index(entry)}), updating refreshed_on...')
                    duplicate_article.refreshed_on = CURRENT_REFRESH_TIME
                else:
                    new_article = Article(title=entry.title,
                                          link=entry.link,
                                          refreshed_on=CURRENT_REFRESH_TIME,
                                          topic=feed.topic,
                                          rssfeed=feed)
                    db.session.add(new_article)
                    logging.debug(f'Added Article ({entries.index(entry)})')


    # Commit changes to the database
    db.session.commit()
    logging.debug('Database refresh complete.')
