"""
This Test suite houses the category endpoint tests
"""
import json
# from werkzeug.datastructures import Headers
from flask_testing import TestCase
from app import APP
from app.models import db, Category
from .test_auth import BaseTestCase

# Test Helpers
from .helpers import register_user, login_user, test_category

class CategoryTestCase(BaseTestCase):
    """This class contains the tests for the categories namespace"""

    def test_category_creation(self):
        """Ensures category can be created"""

        with self.client:
            register_resp = register_user(self)
            self.assertEqual(register_resp.status_code, 201)
            login_resp = login_user(self)
            self.assertEqual(login_resp.status_code, 200)
            # h = Headers()
            # h.add("Authorization", login_resp_data['access_token'] )
            access_token = json.loads(login_resp.data.decode())['access_token']
            response = self.client.post('/category', headers=dict(
                Authorization=access_token
            ), data=test_category, content_type='application/json')
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response_data['status'], "Success!")

    def test_category_duplication(self):
        """Ensures category can be created"""

        with self.client:
            register_resp = register_user(self)
            self.assertEqual(register_resp.status_code, 201)
            login_resp = login_user(self)
            self.assertEqual(login_resp.status_code, 200)
            access_token = json.loads(login_resp.data.decode())['access_token']
            response = self.client.post('/category', headers=dict(
                Authorization=access_token
            ), data=test_category, content_type='application/json')
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response_data['status'], "Success!")
            response = self.client.post('/category', headers=dict(
                Authorization=access_token
            ), data=test_category, content_type='application/json')
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response_data['status'], "Fail!")
            self.assertEqual(response_data['message'], "The category already exists!")

    def test_unauthorized_category_creation(self):
        """Ensures that only logged in users can create cartegories"""

        with self.client:
            # Ensure that resource can not be accessed without an access token
            response = self.client.post('/category', data=test_category, content_type='application/json')
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response_data['status'], "Fail!")
            self.assertEqual(response_data['message'], "Please provide an access token!")
            # Ensure that access is only granted when the right access token is provided (on login)
            response = self.client.post(
                '/category', headers=dict(Authorization="some458273487WRGWU"),
                data=test_category, content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response_data['status'], "Fail!")
            self.assertEqual(response_data['message'], "Login to use this resource!")
