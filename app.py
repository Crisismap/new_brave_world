# -*- coding: utf-8 -*-
import datetime
import os
import re

from flask import Flask, flash, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap

basedir = os.path.abspath(os.path.dirname(__file__))
SQLITE_PREFIX = "sqlite:///" 
name = "data.sqlite"
bd_fname = os.path.join(basedir, "data.sqlite")
bd_full = SQLITE_PREFIX + bd_fname

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = bd_full
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "Haskell"
db = SQLAlchemy(app)
Bootstrap(app)

#with flask-migrate, you can update db schema with such commands:
#export FLASK_APP=app.py; flask db init; flask db migrate; flask db upgrade
migrage = Migrate(app, db)

class News(db.Model):
    __tablename__ = "news"
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    link = db.Column(db.String)

    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    tag = db.relationship('Tag', backref = db.backref('news', lazy = "dynamic"))


    def __init__(self, title, description, link, tag, date= None):
        self.title = title
        self.description = description
        self.link = link
        self.tag = tag
        if date:
            self.date = date
        else:
            self.date = datetime.datetime.utcnow()

    def __repr__(self):
        return "<News %r>" % self.title


class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)

    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return "<Tag %r>" %self.name


#the function is limited by number of items returned by get_sources
def insert_data():
    from get_sources import get_sources
    for tag, news in get_sources(limit = 5):
        with db.session.no_autoflush:
            tag_obj = Tag.query.filter_by(name = tag).first()
            if tag_obj is None:
                tag_obj = Tag(tag)
                db.session.add(tag_obj)
            
            n = News(title = news.title,
                    description = news.description,
                    link = news.link,
                    tag = tag_obj)
            db.session.add(n)
        db.session.commit()

#Some mock function for testing purposes
def query():
    for n in News.query.all():
        print n
    
    #for t in Tag.query.all():
        #for news in t.news.all():
           # print news.link

def b(txt, word):
    return txt.replace(word, u"<b>{word}</b>".format(word = word))

@app.route("/<word>")
def word(word):
    news =  News.query.filter(News.title.like(u"%{word}%".format(word = word)))
    #news =  News.query.filter(or_ (News.title.like(u"%{word}%".format(word = word)),
    #                               News.title.like(u"%{word}%".format(word = word.lower())),
    #                               News.title.like(u"%{word}%".format(word = word.capitalize()))
    #                        ))
    titles = [b(n.title, word) for n in news]
    ns = zip(news, titles)
    return render_template("index.html", news = news, titles = titles, ns = ns)


@app.route("/")
def index():
    return "Hello"

db.drop_all()
db.create_all()
insert_data()

port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)

