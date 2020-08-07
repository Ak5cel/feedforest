# FeedForest

FeedForest is a simple newsfeed subscription service. Stay up-to-date on news/articles from your favourite sites
with a single account.

> *A work in progress.*<br>
> Currently supports subscription from a curated list of feeds. Ability to subscribe to RSS feeds besides the 
available ones is to be added soon. Until then, if you do not find the site you like, let me know :)

### Features
  - A database of articles from a collection of feeds, refreshed every hour
  - Customisable feed wall
  - Bookmark the articles for later
  - Opt-in for a daily email with updates, at the time of your choice

### Dependencies
  - [Flask-SQLAlchemy](https://github.com/pallets/flask-sqlalchemy) - ORM
  - [Flask-Migrate](https://github.com/miguelgrinberg/Flask-Migrate) - Handles database migrations using Alembic, 
    to make changes to the schema without losing existing data
  - [Flask-WTF](https://github.com/lepture/flask-wtf) and [WTForms](https://github.com/wtforms/wtforms) - Form handling
  - [Flask-Login](https://github.com/maxcountryman/flask-login) - Handles user logins and sessions
  - [Jinja2](https://github.com/pallets/jinja) - Template engine
  - [feedparser](https://github.com/kurtmckee/feedparser) - To parse RSS feeds into Python dictionaries
  - [celery](https://github.com/celery/celery) - Distributed task queue. Used for asynchronous background tasks 
    like hourly database refreshes, and sending scheduled emails.
  

### Todo:
  - Ability to subscribe to RSS feeds besides the curated ones available.
  - Support for websites that do not have RSS feeds and provide APIs instead.
  - An API for the website.

...

#### A Note:
> This is my very first Flask project, so all suggestions/advice are welcome and much appreciated!
