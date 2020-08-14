import os
import csv
from src import db
from src.models import Topic, RSSFeed


def add_new_feeds(filename='new-feeds.csv'):
    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)
    path_to_csv = os.path.join(dir_path, filename)
    print(path_to_csv)
    with open(path_to_csv) as file:
        reader = csv.DictReader(file, fieldnames=['topic_name', 'feed_name', 'rss_link', 'site_url'])

        for row in reader:
            feed_exists = RSSFeed.query.filter_by(rss_link=row['rss_link']).first()
            if feed_exists:
                continue
            topic = Topic.query.filter_by(topic_name=row['topic_name']).first()
            if topic is None:
                topic = Topic(topic_name=row['topic_name'])
                db.session.add(topic)
            new_feed = RSSFeed(rss_link=row['rss_link'],
                               site_name=row['feed_name'],
                               site_url=row['site_url'],
                               topic=topic)
            db.session.add(new_feed)

    db.session.commit()
