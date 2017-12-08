"""The API routes"""
import sys
from functools import wraps
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from flask import jsonify, request, make_response
from flask_restplus import Resource
from flask_jwt import jwt, jwt_required

from app import APP
from .restplus import API
from .models import db, User, BlacklistToken
from .serializers import add_user, login_user, password_reset
from .parsers import auth_header

user_ns = API.namespace('users', description="User administration operations.")
auth_ns = API.namespace('auth', description="Authentication/Authorization operations.")

# token decode function:
def decode_access_token(access_token):
    """
    Validates the user access token
    :param access_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(access_token, APP.config.get('SECRET_KEY'))
        is_blacklisted_token = BlacklistToken.check_blacklisted(access_token)
        if is_blacklisted_token:
            return 'Token blacklisted. Please log in again.'
        else:
            public_id = payload['sub']
            user = User.query.filter_by(public_id=public_id).first()
            return user.id
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError: 
        return 'Invalid token. Please log in again.'

# Route security decorator
def authorization_required(func):
    """
    Ensures that only authorized users can access 
    certain resources
    """

    @wraps(func)
    def decorated(*args, **kwargs):
        
        token = None

        if 'access_token' in request.headers:
            token = request.headers['access_token']

        if not token:
            return make_response(jsonify({"message": "Please provide an access token!"}), 401)

        result = decode_access_token(token)

        if not isinstance(result, str):
            current_user = User.query.filter_by(id=result).first()
            return func(current_user, *args, **kwargs)
        current_user = None
        return func(current_user, *args, **kwargs)
    return decorated

@auth_ns.route('/register')
class RegisterHandler(Resource):
    """
    This class handles user account creation.
    """

    @API.expect(add_user)
    def post(self):
        """
        Registers a new user account.
        """
        data = request.get_json()

        # Check if user exists
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            try:
                new_user = User(email=data['email'], username=data['username'], password=data['password'])
                db.session.add(new_user)
                db.session.commit()
                return make_response(jsonify({'message': 'Registered successfully!'}), 201)
            except Exception as e: # pragma: no cover
                response = {"message": "Some error occured. Please retry."}
                return make_response(jsonify(response), 501)
        else:
            return make_response(jsonify({'message': 'User already exists. Please Log in instead.'}), 202)

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
        if not login_info: # pragma: no cover
            return make_response(jsonify({'message': 'Input payload validation failed'}), 401)
        try:
            user = User.query.filter_by(email=login_info['email']).first()
            if not user:
                return make_response(jsonify({"message": 'User does not exist!'}), 404)
            if check_password_hash(user.password, login_info['password']):
                payload = {
                    'exp':  datetime.utcnow() + timedelta(minutes=30),
                    'iat': datetime.utcnow(),
                    'sub': user.public_id
                }
                token = jwt.encode(
                    payload,
                    APP.config['SECRET_KEY'],
                    algorithm='HS256'
                )
                return jsonify({"message": "Logged in successfully.",
                                "access_token": token.decode('UTF-8')
                               })
            return make_response(jsonify({"message": "Incorrect credentials."}), 401)
        except exec as e: # pragma: no cover
            print(e)
            return make_response(jsonify({"message": "An error occurred. Please try again."}), 501)

@auth_ns.route('/logout')
class LogoutHandler(Resource):
    """
    This class handles user logout
    """

    @API.expect(auth_header, validate=True)
    def post(self):
        """
        Logout route
        """
        access_token = request.headers.get('access_token')
        print(access_token, file=sys.stdout)
        if access_token:
            result = decode_access_token(access_token)
            print(result, file=sys.stdout)
            if not isinstance(result, str):
                # mark the token as blacklisted
                blacklisted_token = BlacklistToken(access_token)
                print(blacklisted_token, file=sys.stdout)
                try:
                    # insert the token
                    db.session.add(blacklisted_token)
                    db.session.commit()
                    response_obj = dict(
                        status="success",
                        message="Logged out successfully."
                    )
                    print(jsonify(response_obj), file=sys.stdout)
                    return make_response(jsonify(response_obj), 200)
                except Exception as e: # pragma: no cover
                    resp_obj = {
                        'status': 'fail',
                        'message': e
                    }
                    return make_response(jsonify(resp_obj), 200)
            else:
                resp_obj = dict(
                    status="fail",
                    message=result
                )
                print(jsonify(resp_obj), file=sys.stdout)
                return make_response(jsonify(resp_obj), 401)
        else:
            response_obj = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(response_obj), 403)

@auth_ns.route('/reset-password')
class PasswordResetResource(Resource):
    """
    This class handles the user password reset request
    """

    @API.expect(password_reset)
    def post(self):
        """
        Reset user password
        """
        # Request data
        data = request.get_json()
        # Get specified user
        user = User.query.filter_by(public_id=data['public_id']).first()

        if user:
            
            if check_password_hash(user.password, data['current_password']):
                user.password = generate_password_hash(data['new_password'])
                db.session.commit()
                resp_obj = dict(
                    status="Success!",
                    message="Password reset successfully!"
                )
                resp_obj = jsonify(resp_obj)
                return make_response(resp_obj, 200)
            resp_obj = dict(
                status="Fail!",
                message="Wrong current password. Try again."
            )
            resp_obj = jsonify(resp_obj)
            return make_response(resp_obj, 401)
        resp_obj = dict(
            status="Fail!",
            message="User doesn't exist, check the Public ID provided!"
        )
        resp_obj = jsonify(resp_obj)
        return make_response(resp_obj, 403)

# ADD the namespaces created to the API
API.add_namespace(auth_ns)
API.add_namespace(user_ns)
API.init_app(APP)
