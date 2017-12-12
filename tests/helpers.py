"""
This are helper methods/functions shared across test cases
"""
from flask import json

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
