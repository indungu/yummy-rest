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
        username_re = re.compile(r"(^\w+$)")

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
        raise ValidationError('Password should be 8 characters or longer.')
    else:
        password_re = re.compile(r"^\S+$")
        valid = re.fullmatch(password_re, data)
        if not valid:
            raise ValidationError(
                'Password should not have spaces.'
            )

# User schema
class UserSchema(Schema):
    """
    This schema leverages the validation error reporting capabilities
    of themarshmallow library to validate user input and generate
    error messages on the fly
    """

    email = fields.Email(required=True, validate=validate_email)
    username = fields.Str(required=True, validate=validate_username)
    password = fields.Str(required=True, validate=validate_password)

def validate_name(name):
    """
    This validates that the name provided meets the set criteria for validity.
    """

    if len(name) < 3:
        raise ValidationError(
            "Name too short. Should be 3 or more characters."
        )
    else:
        name_re = re.compile(r"^[a-zA-Z_.]+$")
        valid = re.fullmatch(name_re, name)
        if not valid:
            raise ValidationError(
                "Name should only contain letters, an underscore and/or a period."
            )

def validate_description(data):
    """
    This validates that the name provided meets the set criteria for validity.
    """

    if len(data) > 50:
        raise ValidationError(
            "Description should not be more than 50 characters long."
        )
    else:
        input_re = re.compile(r"\s")
        valid = re.sub(input_re, '', data)
        if not valid:
            raise ValidationError(
                "You need to provide a valid description."
            )

# Categories Schema
class CategorySchema(Schema):
    """
    This schema validates user input when creating a new category
    """

    category_name = fields.Str(required=True, validate=validate_name)
    description = fields.Str(required=True, validate=validate_description)
