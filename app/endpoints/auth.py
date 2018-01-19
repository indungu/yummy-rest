"""The API routes"""
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from flask import jsonify, request, make_response
from flask_restplus import Resource
from flask_jwt import jwt

from app import APP
from app.helpers import decode_access_token
from app.helpers.validators import UserSchema
from app.restplus import API
from app.models import db, User, BlacklistToken
from app.serializers import add_user, login_user, password_reset

# Linting exceptions

# pylint: disable=C0103
# pylint: disable=W0702
# pylint: disable=W0703
# pylint: disable=E1101
# pylint: disable=R0201

auth_ns = API.namespace('auth', description="Authentication/Authorization operations.")

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

        # Instanciate user schema
        user_schema = UserSchema()
        data, errors = user_schema.load(data)

        if errors:
            response_obj = dict(
                errors=errors
            )
            return make_response(jsonify(response_obj), 422)

        # Check if user exists
        email = data['email'].lower()
        user = User.query.filter_by(email=email).first()
        if not user:
            try:
                new_user = User(
                    email=data['email'], username=data['username'], password=data['password']
                )
                db.session.add(new_user)
                db.session.commit()
                return make_response(jsonify({'message': 'Registered successfully!'}), 201)
            except:
                response = {"message": "Username already taken, please choose another."}
                return make_response(jsonify(response), 401)
        else:
            response = jsonify({'message': 'User already exists. Please Log in instead.'})
            return make_response(response, 400)

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
            return make_response(jsonify({'message': 'Input payload validation failed'}), 400)
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
                                "access_token": token.decode('UTF-8'),
                                "public_id": user.public_id
                               })
            return make_response(jsonify({"message": "Incorrect credentials."}), 401)
        except Exception as e:
            print(e)
            return make_response(jsonify({"message": "An error occurred. Please try again."}), 501)

@auth_ns.route('/logout')
class LogoutHandler(Resource):
    """
    This class handles user logout
    """

    def post(self):
        """
        Logout route
        """
        access_token = request.headers.get('Authorization')
        if access_token:
            result = decode_access_token(access_token)
            if not isinstance(result, str):
                # mark the token as blacklisted
                blacklisted_token = BlacklistToken(access_token)
                try:
                    # insert the token
                    db.session.add(blacklisted_token)
                    db.session.commit()
                    response_obj = dict(
                        status="success",
                        message="Logged out successfully."
                    )
                    return make_response(jsonify(response_obj), 200)
                except Exception as e:
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
