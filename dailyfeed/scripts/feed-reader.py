# ---------------------------------------------------------------
# Collects articles from all the RSS feeds and inserts them into
# the 'article' table.
# ---------------------------------------------------------------

# Logging setup for debugging
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
# Comment this out to enable logging mode
logging.disable(logging.CRITICAL)

from feedparser import parse
from dailyfeed import db
from dailyfeed.models import Topic, RSSFeed, Article

# First, clear all entries from the 'article' table.
# This is so that only the most recent records exist in the table
# TODO: change this so that the previous records are kept temporarily. Only delete
# them once the current script runs successfully.
Article.query.delete()
logging.debug('Cleared previous article records')

# Fetch a list of all topics from the db
topics = Topic.query.all()
logging.debug(f'Fetched topics: {topics}')

# For each topic, fetch a list of corresponding RSS feeds
# from the 'rss_feed' table, parse the feeds and insert the articles
# into the 'article' table
for topic in topics:
    logging.debug(f'Getting feeds for topic: {topic.topic_name}...')
    rssfeeds = RSSFeed.query\
        .filter_by(topic=topic)\
        .all()
    logging.debug(f'Collected feeds: {rssfeeds}')

    for rssfeed in rssfeeds:
        logging.debug(f'Getting articles for rssfeed: {rssfeed}...')
        parsed_feed = parse(rssfeed.rss_link)
        # Extract the first 3 articles from the parsed feed
        entries = parsed_feed.entries[:3]
        logging.debug(f'Collected {len(entries)} entries')
        logging.debug(f'Entry 0: {entries[0].title}')
        logging.debug(f'Entry 1: {entries[1].title}')
        logging.debug(f'Entry 2: {entries[2].title}')

        # Create 3 article records
        article1 = Article(title=entries[0].title,
                           link=entries[0].link,
                           topic=topic,
                           rssfeed=rssfeed)
        article2 = Article(title=entries[1].title,
                           link=entries[1].link,
                           topic=topic,
                           rssfeed=rssfeed)
        article3 = Article(title=entries[2].title,
                           link=entries[2].link,
                           topic=topic,
                           rssfeed=rssfeed)
        db.session.add(article1)
        db.session.add(article2)
        db.session.add(article3)

# Commit changes to the tables
db.session.commit()
