"""Data models module"""

from flask_sqlalchemy import SQLAlchemy
from app import APP

db = SQLAlchemy(APP)

class User(db.Model):
    """User model"""

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Category(db.Model):
    """Categories Model"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    description = db.Column(db.String(40), unique=True, nullable=False)

class Recipe(db.Model):
    """Recipes Model"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    ingredients = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    category_id = db.Column(
        db.Integer, db.ForeignKey('category.id'), nullable=False
    )
    category = db.relationship('Category', backref=db.backref('recipes', lazy=True))
