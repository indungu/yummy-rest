"""Main APP module"""
import os
from flask import Flask, make_response, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy

# Linting exception
# pylint: disable=C0103
# pylint: disable=C0413

# local import
from instance.config import app_config


# initialize sql-alchemy
db = SQLAlchemy()

# Get the instance config to use
config_name = os.environ.get("APP_CONFIG", "production")
APP = Flask(__name__, instance_relative_config=True)
APP.config.from_object(app_config[config_name])

# overide 404 error handler

@APP.errorhandler(404)
def resource_not_found(error):
    """
    This will be response returned if the user attempts to access
    a non-existent resource or url.
    """

    response_payload = dict(
        message="The requested URL was not found on the server. " + \
                 "If you entered the URL manually please check your spelling and try again."
    )
    return make_response(jsonify(response_payload), 404)

@APP.route('/', methods=['GET'])
def redirect_to_docs():
    """
    Redirects root to API docs
    """
    return redirect('/api/v1/docs')

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
