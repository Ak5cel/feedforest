from src import db
from src.models import Topic, RSSFeed, Article
topics = [
    {
        "topic_name": "News",
        "sites": [
            {
                "site_name": "New York Times",
                "url": "https://www.nytimes.com",
                "rss_link": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
            },
            {
                "site_name": "BBC News",
                "url": "https://www.bbc.co.uk",
                "rss_link": "http://feeds.bbci.co.uk/news/rss.xml?edition=uk"
            },
            {
                "site_name": "The Independent",
                "url": "https://www.independent.co.uk",
                "rss_link": "http://www.independent.co.uk/news/uk/rss"
            }
        ]
    },
    {
        "topic_name": "Technology",
        "sites": [
            {
                "site_name": "The Verge",
                "url": "https://www.theverge.com",
                "rss_link": "https://www.theverge.com/rss/breaking/index.xml"
            },
            {
                "site_name": "TechCrunch",
                "url": "https://www.techcrunch.com",
                "rss_link": "http://feeds.feedburner.com/TechCrunch/"
            },
            {
                "site_name": "Wired",
                "url": "https://www.wired.com",
                "rss_link": "https://www.wired.com/feed/rss"
            }
        ]
    },
    {
        "topic_name": "Health",
        "sites": [
            {
                "site_name": "Medical News Today",
                "url": "https://www.medicalnewstoday.com/",
                "rss_link": "https://rss.medicalnewstoday.com/featurednews.xml"
            },
            {
                "site_name": "MayoClinic",
                "url": "https://www.mayoclinic.org/",
                "rss_link": "https://www.mayoclinic.org/rss/all-news"
            }
        ]
    }
]

# Add all topics to Topic
for topic in topics:
	newtp = Topic(topic_name=topic['topic_name'])
	db.session.add(newtp)

# Add all sites to RSSFeed

# Adding News-related feeds
data = topics[0]['sites']
# Script to create db and initialise with topics and their rssfeeds

for site in data:
	newfeed = RSSFeed(rss_link=site['rss_link'],
		site_name=site['site_name'],
		site_url=site['url'],
		topic=Topic.query.get(1))
db.session.add(newfeed)

# Adding Technology-related feeds
data = topics[1]['sites']
for site in data:
        newfeed = RSSFeed(rss_link=site['rss_link'],
                site_name=site['site_name'],
                site_url=site['url'],
                topic=Topic.query.get(2))
db.session.add(newfeed)

# Adding Health-related feeds
data = topics[2]['sites']
for site in data:
        newfeed = RSSFeed(rss_link=site['rss_link'],
                site_name=site['site_name'],
                site_url=site['url'],
                topic=Topic.query.get(3))
db.session.add(newfeed)

db.session.commit()
