"""
This package contains the helper functions
"""
import re
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
            response_payload = {
                "message": "Please provide an access token!"
            }
            return make_response(jsonify(response_payload), 401)

        result = decode_access_token(token)

        if not isinstance(result, str):
            current_user = User.query.filter_by(id=result).first()
            return func(current_user, *args, **kwargs)
        current_user = None
        return func(current_user, *args, **kwargs)
    return decorated

# sets the naming convention to be used
def _clean_name(name):
    """
    This function sets the name of a recipe to the standard naming
    convention specified
    """

    name = re.sub(r'\s', "_", name)
    return name.lower()

# Pagination details
def _pagination(paginate, base_url, q=None): # pragma: no cover
    """
    :param paginate: a instance of the Pagination class with paginated query results
    :param base_url: the endpoint url on which the request was made
    :param q: the query string

    :returns pagination_details: a Python dictionary with various pagination details.
    """

    base_url = base_url + "?"
    if q:
        print(q)
        base_url = base_url+"q="+q
    if paginate.has_next:
        next_page = base_url+"&page="+str(paginate.next_num)+"&per_page={}".format(
            str(len(paginate.items))
        )
    else:
        next_page = paginate.next_num
    if paginate.has_prev:
        previous_page = base_url+"&page="+str(paginate.prev_num)+"&per_page={}".format(
            str(len(paginate.items))
        )
    else:
        previous_page = paginate.prev_num
    pagination_details = dict(
        pages=paginate.pages,
        previous_page=previous_page,
        next_page=next_page,
        item_count=len(paginate.items)
    )
    return pagination_details

# Ensure user is authorized
def is_unauthorized():
    """
    Ensure a user is authorized to access a certain resource
    """
    response_payload = dict(
        message='Invalid token. Login to use this resource!'
    )
    response_payload = jsonify(response_payload)
    return make_response(response_payload, 401)

# Make a response payload
def make_payload(category=None, recipe=None):
    """Returns an appropriate response payload"""
    if recipe:
        return dict(
                    id=recipe.id,
                    name=recipe.name,
                    ingredients=recipe.ingredients,
                    description=recipe.description,
                    date_created=recipe.created_on,
                    date_updated=recipe.updated_on,
                    category_id=recipe.category_id
                   )
    if category:
        return dict(
                    id=category.id,
                    name= category.name,
                    description= category.description,
                    date_created= category.created_on,
                    date_updated= category.updated_on
                   )
