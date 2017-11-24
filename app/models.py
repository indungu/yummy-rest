"""Data models module"""
import uuid
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from app import db

class User(db.Model):
    """User model"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    categories = db.relationship('Category', backref='user', lazy='dynamic')
    recipes = db.relationship('Recipe', backref='user', lazy='dynamic')

    def __init__(self, email, username, password):
        self.public_id = uuid.uuid4()
        self.email = email
        self.username = username
        self.password = generate_password_hash(password, method='pbkdf2:sha256')


class Category(db.Model):
    """Categories Model"""

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(40), unique=True, nullable=False)
    description = db.Column(db.String(40), unique=True, nullable=False)
    recipes = db.relationship('Recipe', backref='category', lazy='dynamic')

class Recipe(db.Model):
    """Recipes Model"""

    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(
        db.Integer, db.ForeignKey('categories.id'), nullable=False
    )
    name = db.Column(db.String(40), unique=True, nullable=False)
    ingredients = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
