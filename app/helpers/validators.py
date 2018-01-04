"""
Input validator functions
"""
import re
from marshmallow import Schema, fields, ValidationError

# Validation functions
# email validator
def validate_email(data):
    """
    Ensures that the email provided is of the acceptable
    format expressed below.
    """

    # set the regex to validate against
    email_re = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z-.]+$)")

    # check email passed and raise error if invalid
    result = re.fullmatch(email_re, data)
    if not result:
        raise ValidationError('{} is not a valid email.'.format(data))

# username validator
def validate_username(data):
    """
    Ensures that the username provided is of the acceptable
    format expressed below.
    """

    # minimum length
    if len(data) >= 3:
        # set the regex to validate against
        username_re = re.compile(r"(^[a-zA-Z0-9]+$)")

        # check email passed and raise error if invalid
        result = re.fullmatch(username_re, data)
        if not result:
            raise ValidationError(
                'Username should only contain letters and numbers.'
            )
    else:
        raise ValidationError(
            'Username should be 3 or more characters long.'
        )

# password validator
def validate_password(data):
    """
    Ensures that the password provided is of the acceptable
    length expressed below.
    """

    # minimum length
    if not len(data) >= 8:
        raise ValidationError('Password should be 8 characters or longer')

# User schema
class UserSchema(Schema):
    """
    This schema leverages the validation functions of the
    marshmallow library to validate user input and generate
    error messages on the fly
    """

    email = fields.Email(required=True, validate=validate_email)
    username = fields.Str(required=True, validate=validate_username)
    password = fields.Str(required=True, validate=validate_password)
