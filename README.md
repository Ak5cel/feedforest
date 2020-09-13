# FeedForest

FeedForest is a simple newsfeed subscription service. Stay up-to-date on news/articles from your favourite sites
with a single account.

### Features
  - Subscribe to your favourite RSS feeds, a selection of feeds from various topics is also available
  - Database of articles refreshed with the latest updates every hour
  - Customisable feed wall for the current contents of subscribed feeds at a glance
  - Bookmark articles for later
  - 'Inbox' view for all articles from each subscribed feed since the day it was selected
  - Opt-in for a daily email with updates, at the time of your choice

### Dependencies
  - [Flask-SQLAlchemy](https://github.com/pallets/flask-sqlalchemy) - ORM
  - [feedparser](https://github.com/kurtmckee/feedparser) - To parse RSS feeds into Python dictionaries
  - [celery](https://github.com/celery/celery) - Distributed task queue. Used for asynchronous background tasks 
    like hourly database refreshes, and sending scheduled emails.
  - [Flask-Migrate](https://github.com/miguelgrinberg/Flask-Migrate) - Handles database migrations using Alembic, 
    to make changes to the schema without losing existing data
  - [Flask-WTF](https://github.com/lepture/flask-wtf) and [WTForms](https://github.com/wtforms/wtforms) - Form handling
  - [Flask-Login](https://github.com/maxcountryman/flask-login) - Handles user logins and sessions
  - [Jinja2](https://github.com/pallets/jinja) - Template engine
  
### Further enhancements:
  - More sort/filter options
  - Mark articles as 'Read' when clicked
  - Support for websites that do not have RSS feeds and provide APIs instead.

...

> This is my very first Flask project, suggestions/advice are welcome, encouraged and much appreciated!
