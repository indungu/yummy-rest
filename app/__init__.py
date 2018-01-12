"""Main APP module"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Linting exception
# pylint: disable=C0103
# pylint: disable=C0413

# local import
from instance.config import app_config


# initialize sql-alchemy
db = SQLAlchemy()

APP = Flask(__name__, instance_relative_config=True)
APP.config.from_object(app_config['development'])
db.init_app(APP)

# Import and add namespaces for the endpoints
from app.restplus import API
from app.endpoints.auth import auth_ns
from app.endpoints.categories import categories_ns
from app.endpoints.recipes import recipes_ns

API.add_namespace(auth_ns)
API.add_namespace(categories_ns)
API.add_namespace(recipes_ns)
API.init_app(APP)
