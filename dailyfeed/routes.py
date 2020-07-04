from flask import render_template, url_for, request, flash, redirect
from feedparser import parse
from dailyfeed import app
from dailyfeed.models import Topic, Article


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == "GET":
        topics = Topic.query.all()
        articles = Article.query.all()
    return render_template('home.html',
                           title='Home',
                           topics=topics,
                           articles=articles,
                           parse=parse)


@app.route('/about')
def about():
    return render_template('about.html', title='About Us')
