"""Api Model serializers"""

from flask_restplus import fields
from .restplus import API

# User model serializer
add_user = API.model('API user', {
    'email': fields.String(required=True, description='User email address'),
    'username': fields.String(required=True, description='Preferred username'),
    'password': fields.String(required=True, description='User password.')
})

login_user = API.model('Login API user', {
    'email': fields.String(required=True, description='User email address'),
    'password': fields.String(required=True, description='User password.')
})

password_reset = API.model('Reset password.', {
    'public_id': fields.String(required=True, description="Public ID for the user."),
    'current_password': fields.String(required=True, description='Current password.'),
    'new_password': fields.String(required=True, description='New password.')
})
