"""
This Test suite houses the category endpoint tests
"""
import sys
import json
# from werkzeug.datastructures import Headers
from flask_testing import TestCase
from app import APP
from app.models import db, Category
from .test_auth import BaseTestCase

# Test Helpers
from .helpers import register_user, login_user, test_category, test_category_update

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
            # Register and login test user
            register_resp = register_user(self)
            self.assertEqual(register_resp.status_code, 201)
            login_resp = login_user(self)
            self.assertEqual(login_resp.status_code, 200)
            # Retrieve access token
            access_token = json.loads(login_resp.data.decode())['access_token']
            # Create the category
            response = self.client.post('/category', headers=dict(
                Authorization=access_token
            ), data=test_category, content_type='application/json')
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response_data['status'], "Success!")
            # Attempt a duplication of the same category
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

    def test_category_view_unregistered_user(self):
        """Ensure that only authorized users can view categories"""

        with self.client:
            # When user provides no access token
            response = self.client.get('/category', content_type='application/json')
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertTrue(response_data['status'] == "Fail!")
            self.assertTrue(response_data['message'] == "Please provide an access token!")
            # When user provides invalid access token
            access_token = "some_funny_token_/$tring/"
            auth_header = dict(Authorization=access_token)
            response = self.client.get(
                '/category', headers=auth_header, content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertTrue(response_data['status'] == "Fail!")
            self.assertEqual(response_data['message'], "Login to use this resource!")

    def test_category_view_registered_user(self):
        """Ensure a registered/logged in user can view their categories"""

        with self.client as test_client:
            register_resp = register_user(self)
            self.assertEqual(register_resp.status_code, 201)
            login_resp = login_user(self)
            self.assert200(login_resp, "User not logged in")
            login_resp_data = json.loads(login_resp.data.decode())
            auth_header = dict(
                Authorization=login_resp_data['access_token']
            )
            response = test_client.get(
                '/category', headers=auth_header, content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data.decode())
            print(response_data, file=sys.stdout)
            self.assertTrue(response_data['message'] == "Success!")
            self.assertTrue(len(response_data['categories']) == 0)
            # Create a test category
            category_resp = self.client.post(
                '/category',
                headers=auth_header,
                data=test_category,
                content_type='application/json'
            )
            self.assertEqual(category_resp.status_code, 201)
            # Ensure category is added
            response = test_client.get(
                '/category', headers=auth_header, content_type='application/json'
            )
            self.assert200(response, "Categories not retrieved")
            response_data = json.loads(response.data.decode())
            self.assertTrue(len(response_data['categories']) == 1)

    def test_single_category_retrieval(self):
        """Ensures that a single category can be retrieved"""

        with self.client as test_client:
            # Set up
            register_resp = register_user(self)
            self.assertEqual(register_resp.status_code, 201)
            login_resp = login_user(self)
            self.assert200(login_resp, "User not logged in!")
            access_token = json.loads(login_resp.data.decode())['access_token']
            auth_header = dict(
                Authorization=access_token
            )
            # Add test category
            cat_create_resp = test_client.post(
                '/category', headers=auth_header, data=test_category,
                content_type='application/json'
            )
            cat_create_resp_data = json.loads(cat_create_resp.data.decode())
            self.assertEqual(cat_create_resp.status_code, 201)
            self.assertEqual(cat_create_resp_data['categories'][0]['category_id'], 1)

            # Ensure that the resource is private
            # Attempt Access with no token
            response = test_client.get('/category/1', content_type='application/json')
            self.assertEqual(response.status_code, 401)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['status'], "Fail!")
            self.assertEqual(response_data['message'], "Please provide an access token!")
            
            # Attempt access with invalid token
            x_access_token = "5u32905ugnw9e8ut025u2"
            x_auth_header = dict(Authorization=x_access_token)
            response = test_client.get(
                '/category/1', headers=x_auth_header, content_type='application/json'
            )
            self.assertEqual(response.status_code, 401)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['status'], "Fail!")
            self.assertEqual(response_data['message'], "Invalid token. Login to use this resource!")

            # Ensure single category can be retrieved
            response = test_client.get(
                '/category/1', headers=auth_header, content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data.decode())
            print(response_data, file=sys.stdout)
            self.assertEqual(response_data['status'], "Success!")
            self.assertTrue(len(response_data['categories']) == 1)
            self.assertEqual(response_data['categories'][0]['category_name'], "Cookies")

            # Attempt retrieval of non-existent category
            response = test_client.get(
                '/category/2', headers=auth_header, content_type='application/json'
            )
            self.assertEqual(response.status_code, 404)
            response_data = json.loads(response.data.decode())
            print(response_data, file=sys.stdout)
            self.assertEqual(response_data['status'], "Fail!")
            self.assertEqual(response_data['message'], "Sorry, category does not exist!")

    def test_single_category_update(self):
        """Ensures that a single category can be retrieved"""

        with self.client as test_client:
            # Set up
            register_resp = register_user(self)
            self.assertEqual(register_resp.status_code, 201)
            login_resp = login_user(self)
            self.assert200(login_resp, "User not logged in!")
            access_token = json.loads(login_resp.data.decode())['access_token']
            auth_header = dict(
                Authorization=access_token
            )
            # Add test category
            cat_create_resp = test_client.post(
                '/category', headers=auth_header, data=test_category,
                content_type='application/json'
            )
            cat_create_resp_data = json.loads(cat_create_resp.data.decode())
            self.assertEqual(cat_create_resp.status_code, 201)
            self.assertEqual(cat_create_resp_data['categories'][0]['category_id'], 1)

            # Ensure that the resource is private
            # Attempt Access with no token
            response = test_client.put(
                '/category/1', data=test_category_update,
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 401)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['status'], "Fail!")
            self.assertEqual(response_data['message'], "Please provide an access token!")
            
            # Attempt access with invalid token
            x_access_token = "5u32905ugnw9e8ut025u2"
            x_auth_header = dict(Authorization=x_access_token)
            response = test_client.put(
                '/category/1', headers=x_auth_header,
                data=test_category_update, content_type='application/json'
            )
            self.assertEqual(response.status_code, 401)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['status'], "Fail!")
            self.assertEqual(response_data['message'], "Invalid token. Login to use this resource!")

            # Ensure single category can be updated
            response = test_client.put(
                '/category/1', headers=auth_header,
                data=test_category_update, content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data.decode())
            print(response_data, file=sys.stdout)
            self.assertEqual(response_data['status'], "Success!")
            self.assertTrue(len(response_data['categories']) == 1)
            self.assertEqual(response_data['categories'][0]['category_name'], "Pies")

            # Attempt update of non-existent category
            response = test_client.put(
                '/category/2', headers=auth_header,
                data=test_category_update, content_type='application/json'
            )
            self.assertEqual(response.status_code, 404)
            response_data = json.loads(response.data.decode())
            print(response_data, file=sys.stdout)
            self.assertEqual(response_data['status'], "Fail!")
            self.assertEqual(response_data['message'], "Sorry, category does not exist!")

    def test_single_category_delete(self):
        """Ensures that a single category can be deleted"""

        with self.client as test_client:
            # Set up
            register_resp = register_user(self)
            self.assertEqual(register_resp.status_code, 201)
            login_resp = login_user(self)
            self.assert200(login_resp, "User not logged in!")
            access_token = json.loads(login_resp.data.decode())['access_token']
            auth_header = dict(
                Authorization=access_token
            )
            # Add test category
            cat_create_resp = test_client.post(
                '/category', headers=auth_header, data=test_category,
                content_type='application/json'
            )
            cat_create_resp_data = json.loads(cat_create_resp.data.decode())
            self.assertEqual(cat_create_resp.status_code, 201)
            self.assertEqual(cat_create_resp_data['categories'][0]['category_id'], 1)

            # Ensure that the resource is private
            # Attempt Access with no token
            response = test_client.delete(
                '/category/1', content_type='application/json'
            )
            self.assertEqual(response.status_code, 401)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['status'], "Fail!")
            self.assertEqual(response_data['message'], "Please provide an access token!")
            
            # Attempt access with invalid token
            x_access_token = "5u32905ugnw9e8ut025u2"
            x_auth_header = dict(Authorization=x_access_token)
            response = test_client.delete(
                '/category/1', headers=x_auth_header, content_type='application/json'
            )
            self.assertEqual(response.status_code, 401)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['status'], "Fail!")
            self.assertEqual(response_data['message'], "Invalid token. Login to use this resource!")

            # Ensure single category can be deleted
            response = test_client.delete(
                '/category/1', headers=auth_header, content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data.decode())
            print(response_data, file=sys.stdout)
            self.assertEqual(response_data['status'], "Success!")

            # Attempt delete of non-existent category
            response = test_client.delete(
                '/category/2', headers=auth_header, content_type='application/json'
            )
            self.assertEqual(response.status_code, 404)
            response_data = json.loads(response.data.decode())
            print(response_data, file=sys.stdout)
            self.assertEqual(response_data['status'], "Fail!")
            self.assertEqual(response_data['message'], "Sorry, category does not exist!")
