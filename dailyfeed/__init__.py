import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), 'app.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db = SQLAlchemy(app)

from dailyfeed import routes
import feedparser
