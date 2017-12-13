"""Data models module"""
import uuid
from datetime import datetime
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
    created_on = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_on = db.Column(
        db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp()
    )
    recipes = db.relationship('Recipe', backref='category', lazy='dynamic')

    def __init__(self, name, owner, description):
        self.name = name
        self.user_id = owner
        self.description = description

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
    created_on = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_on = db.Column(
        db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp()
    )

class BlacklistToken(db.Model):
    """Blacklisted tokens Model"""

    __tablename__ = "blacklist"

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), nullable=False, unique=True)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.utcnow()
    
    def __repr__(self):
        return '<Token: {} Blacklist_date {}>'.format(self.token, self.blacklisted_on)

    @staticmethod
    def check_blacklisted(token):
        # check whether auth token has been blacklisted
        exists = BlacklistToken.query.filter_by(token=str(token)).first()
        if exists:
            return True
        else:
            return False

