"""Main APP module"""

from flask import Flask

APP = Flask(__name__, instance_relative_config=True)

from app import views

APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:password@localhost:5432/yummy_rest_db'
APP.config.from_pyfile('config.py')
