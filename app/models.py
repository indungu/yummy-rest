"""Data models module"""
import uuid
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from app import APP

db = SQLAlchemy(APP)

class User(db.Model):
    """User model"""

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, email, username, password):
        self.public_id = uuid.uuid4()
        self.email = email
        self.username = username
        self.password = generate_password_hash(password, method='pbkdf2:sha256')

    def __repr__(self):
        return "<User %r>" % self.username

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
