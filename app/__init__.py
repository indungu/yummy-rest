"""Main APP module"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# local import
from instance.config import app_config
from app.restplus import API

# initialize sql-alchemy
db = SQLAlchemy()

APP = Flask(__name__, instance_relative_config=True)
APP.config.from_object(app_config['development'])
db.init_app(APP)

from app.api import API
