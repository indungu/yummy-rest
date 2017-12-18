"""
This is the unit test suite for the recipes endpoint
"""
import sys
import json
from flask_testing import TestCase

from app.models import User, Category, Recipe
from .helpers import register_user, login_user, test_category, test_recipe
from .test_auth import BaseTestCase

class RecipesTestCase(BaseTestCase):
    """
    This class contains the tests for the recipe CRUD endpoints
    """

    def set_up(self):
        with self.client as test_client:
            register_resp = register_user(self)
            self.assertEqual(register_resp.status_code, 201)
            login_resp = login_user(self)
            self.assert200(login_resp, "User not logged in")
            login_resp_data = json.loads(login_resp.data.decode())
            self.auth_header = dict(
                Authorization=login_resp_data['access_token']
            )
            category_create_resp = test_client.post(
                '/category', headers=self.auth_header, data=test_category,
                content_type='application/json'
            )
            self.assertEqual(category_create_resp.status_code, 201)

    def test_recipe_create_resource_security(self):
        """
        Ensures that the resource is protected/private
        """
        with self.client as test_client:
            # Test the resouce with No authorization
            response = test_client.post(
                '/category/1/recipes', data=test_recipe,
                content_type='application/json'
            )
            self.assert401(response, "Wrong reponse code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['status'], 'Fail!')
            self.assertEqual(response_data['message'], "Please provide an access token!")
            # test the resource with invalid authorization
            response = test_client.post(
                '/category/1/recipes', headers=dict(Authorization="Some98247982hnidutie3rojgnadf"),
                data=test_recipe, content_type='application/json'
            )            
            self.assert401(response, "Wrong reponse code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['status'], 'Fail!')
            self.assertEqual(response_data['message'], 'Invalid token. Login to use this resource!')

    def test_recipe_creation_invalid_category(self):
        """
        Ensures that if user attempts to add a recipe to a non existent category,
        the action is flagged as an error
        """

        self.set_up()
        with self.client as test_client:
            # when a wrong or invalid category_id is provided
            response = test_client.post(
                'category/2/recipes', headers=self.auth_header,
                data=test_recipe, content_type='application/json'
            )
            self.assert400(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], 'Invalid category!')
            self.assertEqual(response_data['status'], 'Fail!')

    def test_recipe_creation(self):
        """
        Ensures a user can create a recipe in a specified category
        """

        self.set_up()
        with self.client as test_client:
            
            response = test_client.post(
                '/category/1/recipes', headers=self.auth_header,
                data=test_recipe, content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['status'], 'Success!')
            self.assertEqual(len(response_data['recipes']), 1)

    def test_recipe_duplication(self):
        """
        Ensures a user can create a recipe in a specified category
        """

        self.set_up()
        with self.client as test_client:
            # add recipe
            response = test_client.post(
                '/category/1/recipes', headers=self.auth_header,
                data=test_recipe, content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['status'], 'Success!')
            self.assertEqual(len(response_data['recipes']), 1)
            # Duplicate recipe
            response = test_client.post(
                '/category/1/recipes', headers=self.auth_header,
                data=test_recipe, content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['status'], 'Fail!')
            self.assertEqual(response_data['message'], 'Recipe already exists!')

    def test_recipes_view_resource_security(self):
        """
        Ensures the resource is projected from unauthorized access
        """

        with self.client as test_client:
            # Ensure no access without Authorization
            response = test_client.get(
                '/category/1/recipes', content_type='application/json'
            )
            self.assert401(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['status'], 'Fail!')
            self.assertEqual(response_data['message'], "Please provide an access token!")
            # Ensure no access with invalid authorization
            response = test_client.get(
                '/category/1/recipes', headers=dict(Authorization="Some98247982hnidutie3rojgnadf"),
                content_type='application/json'
            )            
            self.assert401(response, "Wrong reponse code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['status'], 'Fail!')
            self.assertEqual(response_data['message'], 'Invalid token. Login to use this resource!')

    def test_recipes_view(self):
        """
        Ensures user can view recipes for a particular category
        """

        self.set_up()
        with self.client as test_client:
            # Retrieval from a valid category with no recipes yet
            response = test_client.get(
                '/category/1/recipes', headers=self.auth_header,
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], 'No recipes added to this category yet!')
            self.assertEqual(response_data['status'], 'Success!')
            # Add test recipe
            add_recipe_resp = test_client.post(
                '/category/1/recipes', headers=self.auth_header,
                data=test_recipe, content_type='application/json'
            )
            self.assertEqual(
                json.loads(add_recipe_resp.data.decode())['status'],
                'Success!'
            )
            # Retrive recipe
            response = test_client.get(
                '/category/1/recipes', headers=self.auth_header,
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['status'], 'Success!')
            self.assertEqual(len(response_data['recipes']), 1)

            # Attempt retrieval from an invalid category
            response = test_client.get(
                '/category/2/recipes', headers=self.auth_header,
                content_type='application/json'
            )
            self.assert400(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['status'], 'Fail!')
            self.assertEqual(response_data['message'], 'Invalid category!')
