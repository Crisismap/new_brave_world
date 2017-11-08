# -*- coding: utf-8 -*-
import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s\t%(levelname)s\t%(filename)s\t%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

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


