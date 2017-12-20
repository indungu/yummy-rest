"""
This are helper methods/functions shared across test cases
"""
from flask import json

# linting exception
# pylint: disable=C0103

# Registration details
user_details = dict(
    email="isaac@yum.my",
    username="isaac",
    password="123456"
)

# Login details
login_details = dict(
    email=user_details['email'],
    password=user_details['password']
)

# Test Category details
test_category = json.dumps(dict(
    category_name="Cookies",
    description="All my cookies recipes."
))

# Test Category update details
test_category_update = json.dumps(dict(
    category_name="Pies",
    description="All my pie recipes."
))

# recipe details
test_recipe = json.dumps(dict(
    recipe_name='Chocolate chip',
    ingredients="Some ingredients here\n\rSome others there.",
    description="Prepare with care and serve with love"
))

# Register test user
def register_user(self):
    """Registers a test user"""
    return self.client.post('/auth/register',
                            data=json.dumps(user_details), content_type='application/json'
                           )

# Login test user
def login_user(self):
    """Logs a user in"""
    return self.client.post('/auth/login',
                            data=json.dumps(login_details), content_type='application/json'
                           )
