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
    # check email is not empty nor too short
    if not data or len(data) < 6:
        raise ValidationError('Email cannot be empty or less than 6 characters long.')
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
    elif not re.search('[a-z]+', data):
        raise ValidationError('Password should have at least one lowercase letter.')
    elif not re.search('[A-Z]+', data):
        raise ValidationError('Password should have at least one uppercase letter.')
    elif not re.search('\W+', data):
        raise ValidationError('Password should have at least one special character.')
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

    if not name:
        raise ValidationError(
            "Name is a required value and cannot be empty."
        )
    elif len(name) < 3:
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

    if not data:
        raise ValidationError(
            "Description is a required value and cannot be empty."
        )
    elif len(data) > 50:
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

def validate_input(data):
    """
    Checks if the input data is valid and not just a series of whitespace
    characters
    """

    if not data:
        raise ValidationError(
            "This is a required value and cannot be empty."
        )
    input_re = re.compile(r"\s")
    valid = re.sub(input_re, '', data)
    if not valid:
        raise ValidationError(
            "Invalid input value."
        )

class RecipeSchema(Schema):
    """
    Validates the input recipe details
    """

    recipe_name = fields.Str(required=True, validate=validate_name)
    ingredients = fields.Str(required=True, validate=validate_input)
    description = fields.Str(required=True, validate=validate_input)
