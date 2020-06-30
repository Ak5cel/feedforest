from flask import Flask

app = Flask(__name__)

from dailyfeed import routes
import feedparser
