"""
This are helper methods/functions shared across test cases
"""
from flask import json

# Register user helper

def register_user(self, email, username, password):
        """Registers a test user"""
        return self.client.post('/auth/register',
                                  data=json.dumps(dict(
                                      email=email,
                                      username=username,
                                      password=password
                                  )), content_type="application/json"
                                 )
