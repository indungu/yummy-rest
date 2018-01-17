"""
This Test suite houses the category endpoint tests
"""
import json
from app.helpers import _clean_name
from .test_auth import BaseTestCase

# Linting exceptions
# pylint: disable=C0103
# pylint: disable=W0201

# Test Helpers
from .helpers import register_user, login_user, test_category, test_category_update, \
                     invalid_category, invalid_category_2

class CategoryTestCase(BaseTestCase):
    """This class contains the tests for the categories namespace"""

    def test_category_creation(self):
        """Ensures category can be created"""

        with self.client:
            register_resp = register_user(self)
            self.assertEqual(register_resp.status_code, 201)
            login_resp = login_user(self)
            self.assertEqual(login_resp.status_code, 200)
            access_token = json.loads(login_resp.data.decode())['access_token']
            response = self.client.post('/api/v1/category', headers=dict(
                Authorization=access_token
            ), data=test_category, content_type='application/json')
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn("category_name", response_data['categories'][0])

    def test_category_creation_invalid_name(self):
        """Ensures category cannot be created with an invalid name"""

        with self.client:
            register_resp = register_user(self)
            self.assertEqual(register_resp.status_code, 201)
            login_resp = login_user(self)
            self.assertEqual(login_resp.status_code, 200)
            access_token = json.loads(login_resp.data.decode())['access_token']
            # Ensure that category name is of a valid length
            response = self.client.post('/api/v1/category', headers=dict(
                Authorization=access_token
            ), data=invalid_category, content_type='application/json')
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 422)
            errors = response_data['errors']
            self.assertTrue(
                'category_name' in errors
            )
            self.assertEqual(
                errors['category_name'][0], 'Name too short. Should be 3 or more characters.'
            )
            # Ensure that category name is of a valid format
            response = self.client.post('/api/v1/category', headers=dict(
                Authorization=access_token
            ), data=invalid_category_2, content_type='application/json')
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 422)
            errors = response_data['errors']
            self.assertTrue(
                'category_name' in errors
            )
            self.assertEqual(
                errors['category_name'][0],
                "Name should only contain letters, an underscore and/or a period."
            )

    def test_category_creation_invalid_description(self):
        """Ensures category cannot be created with an invalid description"""

        with self.client:
            register_resp = register_user(self)
            self.assertEqual(register_resp.status_code, 201)
            login_resp = login_user(self)
            self.assertEqual(login_resp.status_code, 200)
            access_token = json.loads(login_resp.data.decode())['access_token']
            # Ensure that category description is of a valid length
            response = self.client.post('/api/v1/category', headers=dict(
                Authorization=access_token
            ), data=invalid_category, content_type='application/json')
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 422)
            errors = response_data['errors']
            self.assertTrue(
                'category_name' in errors
            )
            self.assertEqual(
                errors['description'][0], 'Description should not be more than 50 characters long.'
            )
            # Ensure that category name is of a valid format
            response = self.client.post('/api/v1/category', headers=dict(
                Authorization=access_token
            ), data=invalid_category_2, content_type='application/json')
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 422)
            errors = response_data['errors']
            self.assertTrue(
                'description' in errors
            )
            self.assertEqual(
                errors['description'][0],
                "You need to provide a valid description."
            )

    def test_category_duplication(self):
        """Ensures category cannot be duplicated"""

        with self.client:
            # Register and login test user
            register_resp = register_user(self)
            self.assertEqual(register_resp.status_code, 201)
            login_resp = login_user(self)
            self.assertEqual(login_resp.status_code, 200)
            # Retrieve access token
            access_token = json.loads(login_resp.data.decode())['access_token']
            # Create the category
            response = self.client.post('/api/v1/category', headers=dict(
                Authorization=access_token
            ), data=test_category, content_type='application/json')
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            # Attempt a duplication of the same category
            response = self.client.post('/api/v1/category', headers=dict(
                Authorization=access_token
            ), data=test_category, content_type='application/json')
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response_data['message'], "The category already exists!")

    def test_unauthorized_category_creation(self):
        """Ensures that only logged in users can create cartegories"""

        with self.client:
            # Ensure that resource can not be accessed without an access token
            response = self.client.post(
                '/api/v1/category', data=test_category, content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response_data['message'], "Please provide an access token!")
            # Ensure that access is only granted when the right access token is provided (on login)
            response = self.client.post(
                '/api/v1/category', headers=dict(Authorization="some458273487WRGWU"),
                data=test_category, content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response_data['message'], "Login to use this resource!")

    def test_category_view_unregistered_user(self):
        """Ensure that only authorized users can view categories"""

        with self.client:
            # When user provides no access token
            response = self.client.get('/api/v1/category', content_type='application/json')
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertTrue(response_data['message'] == "Please provide an access token!")
            # When user provides invalid access token
            access_token = "some_funny_token_/$tring/"
            auth_header = dict(Authorization=access_token)
            response = self.client.get(
                '/api/v1/category', headers=auth_header, content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
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
                '/api/v1/category', headers=auth_header, content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data.decode())
            self.assertTrue(response_data['message'] == "No categories exist. Please create some.")
            # Create a test category
            category_resp = self.client.post(
                '/api/v1/category',
                headers=auth_header,
                data=test_category,
                content_type='application/json'
            )
            self.assertEqual(category_resp.status_code, 201)
            # Ensure category is added
            response = test_client.get(
                '/api/v1/category', headers=auth_header, content_type='application/json'
            )
            self.assert200(response, "Categories not retrieved")
            response_data = json.loads(response.data.decode())
            self.assertTrue(len(response_data['categories']) == 1)

    def test_category_view_with_search_and_pagination(self):
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
            # Add a test categories
            category_resp = self.client.post(
                '/api/v1/category',
                headers=auth_header,
                data=test_category,
                content_type='application/json'
            )
            self.assertEqual(category_resp.status_code, 201)
            category_resp = self.client.post(
                '/api/v1/category',
                headers=auth_header,
                data=test_category_update,
                content_type='application/json'
            )
            self.assertEqual(category_resp.status_code, 201)
            # Default get without any search or pagination parameters defined
            response = test_client.get(
                '/api/v1/category', headers=auth_header, content_type='application/json'
            )
            self.assert200(response, "Categories not retrieved")
            response_data = json.loads(response.data.decode())
            self.assertTrue(len(response_data['categories']) == 2)
            self.assertTrue('page_details' in response_data)
            self.assertEqual(response_data['page_details']['pages'], 1)
            # When only pagination args are defined
            response = test_client.get(
                '/api/v1/category?page=1&per_page=1',
                headers=auth_header,
                content_type='application/json'
            )
            self.assert200(response, "Categories not retrieved")
            response_data = json.loads(response.data.decode())
            self.assertEqual(len(response_data['categories']), 1)
            self.assertEqual(response_data['categories'][0]['category_name'], "cookies")
            self.assertTrue('page_details' in response_data)
            self.assertEqual(response_data['page_details']['pages'], 2)

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
                '/api/v1/category', headers=auth_header, data=test_category,
                content_type='application/json'
            )
            cat_create_resp_data = json.loads(cat_create_resp.data.decode())
            self.assertEqual(cat_create_resp.status_code, 201)
            self.assertEqual(cat_create_resp_data['categories'][0]['category_id'], 1)

            # Ensure that the resource is private
            # Attempt Access with no token
            response = test_client.get('/api/v1/category/1', content_type='application/json')
            self.assertEqual(response.status_code, 401)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], "Please provide an access token!")

            # Attempt access with invalid token
            x_access_token = "5u32905ugnw9e8ut025u2"
            x_auth_header = dict(Authorization=x_access_token)
            response = test_client.get(
                '/api/v1/category/1', headers=x_auth_header, content_type='application/json'
            )
            self.assertEqual(response.status_code, 401)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], "Invalid token. Login to use this resource!")

            # Ensure single category can be retrieved
            response = test_client.get(
                '/api/v1/category/1', headers=auth_header, content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data.decode())
            self.assertTrue(len(response_data['categories']) == 1)
            self.assertEqual(response_data['categories'][0]['category_name'], "cookies")

            # Attempt retrieval of non-existent category
            response = test_client.get(
                '/api/v1/category/2', headers=auth_header, content_type='application/json'
            )
            self.assertEqual(response.status_code, 404)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], "Sorry, category does not exist!")

    def test_single_category_update(self):
        """Ensures that a single category can be updated"""

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
                '/api/v1/category', headers=auth_header, data=test_category,
                content_type='application/json'
            )
            cat_create_resp_data = json.loads(cat_create_resp.data.decode())
            self.assertEqual(cat_create_resp.status_code, 201)
            self.assertEqual(cat_create_resp_data['categories'][0]['category_id'], 1)

            # Ensure that the resource is private
            # Attempt Access with no token
            response = test_client.put(
                '/api/v1/category/1', data=test_category_update,
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 401)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], "Please provide an access token!")

            # Attempt access with invalid token
            x_access_token = "5u32905ugnw9e8ut025u2"
            x_auth_header = dict(Authorization=x_access_token)
            response = test_client.put(
                '/api/v1/category/1', headers=x_auth_header,
                data=test_category_update, content_type='application/json'
            )
            self.assertEqual(response.status_code, 401)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], "Invalid token. Login to use this resource!")

            # Ensure single category can be updated with a complete set of
            # new details
            response = test_client.put(
                '/api/v1/category/1', headers=auth_header,
                data=test_category_update, content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data.decode())
            self.assertEqual(
                response_data['message'],
                "Category '{}' was successfully updated to '{}'.".format(
                    _clean_name(json.loads(test_category)['category_name']),
                    _clean_name(json.loads(test_category_update)['category_name'])
                )
            )

            # Ensure single category can be updated with a new description only
            json.loads(test_category_update)['description'] = "Some new description"
            response = test_client.put(
                '/api/v1/category/1', headers=auth_header,
                data=test_category_update, content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data.decode())
            self.assertEqual(
                response_data['message'],
                "Category '{}' was successfully updated.".format(
                    _clean_name(json.loads(test_category_update)['category_name'])
                )
            )

            # Attempt update of non-existent category
            response = test_client.put(
                '/api/v1/category/2', headers=auth_header,
                data=test_category_update, content_type='application/json'
            )
            self.assertEqual(response.status_code, 404)
            response_data = json.loads(response.data.decode())
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
                '/api/v1/category', headers=auth_header, data=test_category,
                content_type='application/json'
            )
            cat_create_resp_data = json.loads(cat_create_resp.data.decode())
            self.assertEqual(cat_create_resp.status_code, 201)
            self.assertEqual(cat_create_resp_data['categories'][0]['category_id'], 1)

            # Ensure that the resource is private
            # Attempt Access with no token
            response = test_client.delete(
                '/api/v1/category/1', content_type='application/json'
            )
            self.assertEqual(response.status_code, 401)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], "Please provide an access token!")

            # Attempt access with invalid token
            x_access_token = "5u32905ugnw9e8ut025u2"
            x_auth_header = dict(Authorization=x_access_token)
            response = test_client.delete(
                '/api/v1/category/1', headers=x_auth_header, content_type='application/json'
            )
            self.assertEqual(response.status_code, 401)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], "Invalid token. Login to use this resource!")

            # Ensure single category can be deleted
            response = test_client.delete(
                '/api/v1/category/1', headers=auth_header, content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data.decode())
            self.assertEqual(
                response_data['message'],
                "Category '{}' was deleted successfully.".format(
                    _clean_name(json.loads(test_category)['category_name'])
                )
            )

            # Attempt delete of non-existent category
            response = test_client.delete(
                '/api/v1/category/2', headers=auth_header, content_type='application/json'
            )
            self.assertEqual(response.status_code, 404)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], "Sorry, category does not exist!")
