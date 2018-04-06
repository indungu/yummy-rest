"""Api Model serializers"""

from flask_restplus import fields
from .restplus import API

# Linting exception
# pylint: disable=C0103

# User model serializer
add_user = API.model('API user', {
    'email': fields.String(
        required=True, description='User email address', example="user@domain.com"
    ),
    'username': fields.String(required=True, description='Preferred username', example="user"),
    'password': fields.String(required=True, description='User password.', example="someP@ss")
})

login_user = API.model('Login API user', {
    'email': fields.String(
        required=True, description='User email address', example="user@domain.com"
    ),
    'password': fields.String(required=True, description='User password.', example="somep@ss")
})

password_reset = API.model('Reset password.', {
    'public_id': fields.String(required=True, description="Public ID for the user."),
    'current_password': fields.String(required=True, description='Current password.'),
    'new_password': fields.String(required=True, description='New password.')
})

category = API.model('Recipe Category', {
    'name': fields.String(required=True, description='Name of the recipe category'),
    'description': fields.String(required=True, description='A slight description of the category')
})

recipe = API.model('Recipe', {
    'name': fields.String(required=True, description='Name of the recipe'),
    'ingredients': fields.String(required=True, description='All the necessary ingredients'),
    'description': fields.String(required=True, description='The instruction on preparation')
})
