"""The API routes"""
from flask import jsonify
from .models import User, Category, Recipe

from app import APP

@APP.route('/', methods=['GET'])
def index():
    """Index route"""
    return jsonify({"message": "Welcome to Yummy Recipes REST API!"})
