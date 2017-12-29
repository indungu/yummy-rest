"""
This package contains the helper functions
"""

from functools import wraps
from flask import jsonify, request, make_response
from flask_jwt import jwt

from app import APP
from app.models import db, User, BlacklistToken

# token decode function:
def decode_access_token(access_token):
    """
    Validates the user access token

    :param str access_token: The access token tp be decoded
    :return: integer|string
    """
    try:
        payload = jwt.decode(access_token, APP.config.get('SECRET_KEY'))
        is_blacklisted_token = BlacklistToken.check_blacklisted(access_token)
        if is_blacklisted_token:
            return 'Token blacklisted. Please log in again.'
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

        """
        Resource security decorator function
        """
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization']

        if not token:
            response_obj = {
                "message": "Please provide an access token!",
                "status": "Fail!"
            }
            return make_response(jsonify(response_obj), 401)

        result = decode_access_token(token)

        if not isinstance(result, str):
            current_user = User.query.filter_by(id=result).first()
            return func(current_user, *args, **kwargs)
        current_user = None
        return func(current_user, *args, **kwargs)
    return decorated
