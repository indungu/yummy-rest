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
    password="1234509876"
)

# Registration details with invalid email
user_details_inv_email = dict(
    email="isaac@yummy",
    username="isaac",
    password="1234509876"
)

# Registration details with invalid username
# with special characters
user_details_inv_username = dict(
    email="isaac@yummy",
    username="is@@c",
    password="1234509876"
)
# invalid length
user_details_inv_username_2 = dict(
    email="isaac@yummy",
    username="@c",
    password="1234509876"
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

# update recipe details
test_recipe_update = json.dumps(dict(
    recipe_name='Mint Chocolate chip',
    ingredients="Some ingredients there\n\rSome others here.",
    description="Prepare with love and serve with care"
))

# Register test user
def register_user(self, user_data=user_details):
    """Registers a test user"""
    return self.client.post('/auth/register',
                            data=json.dumps(user_data), content_type='application/json'
                           )

# Login test user
def login_user(self):
    """Logs a user in"""
    return self.client.post('/auth/login',
                            data=json.dumps(login_details), content_type='application/json'
                           )
