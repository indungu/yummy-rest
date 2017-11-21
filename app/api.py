"""The API routes"""
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
from flask import jsonify, request, make_response
from flask_restplus import Resource
from flask_jwt import jwt, jwt_required
from app import APP
from .restplus import API
from .models import db, User
from .serializers import add_user, login_user
user_ns = API.namespace('users', description="User administration operations.")
auth_ns = API.namespace('auth', description="Authentication/Authorization operations.")

@user_ns.route('/')
class GeneralUserHandler(Resource):
    def get(self):
        """
        Returns all the users in the database
        """

        users = User.query.all()
        if users:
            output = []
            for user in users:
                user_data = {}
                user_data['email'] = user.email
                user_data['password'] = user.password
                user_data['public_id'] = user.public_id
                user_data['username'] = user.username
                output.append(user_data)
            return jsonify({"users": output})
        return jsonify({"message": "No user(s) added!"})

@user_ns.route('/<public_id>')
class SpecUserHandler(Resource):
    
    def get(self, public_id):
        """
        Gets a single user to admin
        """
        user = User.query.filter_by(public_id=public_id).first()

        if not user:
            return jsonify({"message": "No user found!"})

        user_data = {}
        user_data['email'] = user.email
        user_data['password'] = user.password
        user_data['public_id'] = user.public_id
        user_data['username'] = user.username
        return jsonify({"user": user_data})
    

    def delete(self, public_id):
        """
        Removes a user account
        """
        user = User.query.filter_by(public_id=public_id).first()

        if not user:
            return jsonify({"message": "No user found!"})

        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User was deleted!"})

@auth_ns.route('/register')
class RegisterHandler(Resource):
    """
    This class handles user account creation.
    """

    @API.response(201, 'User successfully created.')
    @API.expect(add_user)
    def post(self):
        """
        Registers a new user account.
        """
        data = request.get_json()
        new_user = User(email=data['email'], username=data['username'], password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'New User created!'})

@auth_ns.route('/login')
class LoginHandler(Resource):
    """
    This class handles user login
    """

    @API.expect(login_user)
    def post(self):
        """
        User Login/SignIn route
        """
        login_info = request.get_json()
        if not login_info:
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login require!"'})
        user = User.query.filter_by(email=login_info['email']).first()
        if not user:
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login require!"'})
        if check_password_hash(user.password, login_info['password']):
            token = jwt.encode(
                {'public_id': user.public_id, 'exp': datetime.utcnow() + timedelta(minutes=30)},
                APP.config['SECRET_KEY']
            )
            return jsonify({"access_token": token.decode('UTF-8')})
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login require!"'})
