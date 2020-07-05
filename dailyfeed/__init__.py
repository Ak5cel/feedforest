import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dailyfeed.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from dailyfeed import routes
import feedparser
