"""Main APP module"""

from flask import Flask

APP = Flask(__name__, instance_relative_config=True)

from app.api import API

APP.config.from_pyfile('config.py')
