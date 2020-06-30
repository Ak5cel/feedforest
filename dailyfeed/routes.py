from flask import render_template, url_for
from feedparser import parse
from dailyfeed import app


# TODO: Change to query results later
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
                "rss_link": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
            },
            {
                "site_name": "TechCrunch",
                "url": "https://www.techcrunch.com",
                "rss_link": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
            },
            {
                "site_name": "Wired",
                "url": "https://www.wired.com",
                "rss_link": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
            }
        ]
    },
    {
        "topic_name": "Health",
        "sites": [
            {
                "site_name": "Harvard Health",
                "url": "https://www.health.harvard.edu",
                "rss_link": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
            },
            {
                "site_name": "WebMD",
                "url": "https://www.webmd.com",
                "rss_link": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
            }
        ]
    }
]


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Home', topics=topics, parse=parse)


@app.route('/about')
def about():
    return render_template('about.html', title='About Us')
