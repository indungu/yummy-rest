"""
This is the unit test suite for the recipes endpoint
"""
import json
from app.helpers import _clean_name
from .test_auth import BaseTestCase
from .helpers import register_user, login_user, test_category, test_recipe, test_recipe_update,\
                     invalid_recipe

# Linting exceptions
# pylint: disable=C0103
# pylint: disable=W0201

class RecipesTestCase(BaseTestCase):
    """
    This class contains the tests for the recipe CRUD endpoints
    """

    def set_up(self):
        """
        Custom test setup
        """
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
                '/api/v1/category', headers=self.auth_header, data=test_category,
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
                '/api/v1/category/1/recipes', data=test_recipe,
                content_type='application/json'
            )
            self.assert401(response, "Wrong reponse code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], "Please provide an access token!")
            # test the resource with invalid authorization
            response = test_client.post(
                '/api/v1/category/1/recipes',
                headers=dict(Authorization="Some98247982hnidutie3rojgnadf"),
                data=test_recipe, content_type='application/json'
            )
            self.assert401(response, "Wrong reponse code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
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
                '/api/v1/category/2/recipes', headers=self.auth_header,
                data=test_recipe, content_type='application/json'
            )
            self.assert400(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], 'Invalid category!')

    def test_recipe_creation_valid_category(self):
        """
        Ensures a user can create a recipe in a specified category
        """

        self.set_up()
        with self.client as test_client:

            response = test_client.post(
                '/api/v1/category/1/recipes', headers=self.auth_header,
                data=test_recipe, content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)
            response_data = json.loads(response.data.decode())
            self.assertEqual(len(response_data['recipes']), 1)

    def test_recipe_creation_valid_category_invalid_name(self):
        """
        Ensures a user cannot create a recipe in a specified category
        with invalid recipe details
        """

        self.set_up()
        with self.client as test_client:

            # When the recipe name is
            # of invalid length
            response = test_client.post(
                '/api/v1/category/1/recipes', headers=self.auth_header,
                data=invalid_recipe, content_type='application/json'
            )
            self.assertEqual(response.status_code, 422)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], 'You provided some invalid details.')
            errors = response_data['errors']
            self.assertTrue(
                'name' in errors
            )
            self.assertEqual(
                errors['name'][0], "Name too short. Should be 3 or more characters."
            )

    def test_recipe_duplication(self):
        """
        Ensures a user can create a recipe in a specified category
        """

        self.set_up()
        with self.client as test_client:
            # add recipe
            response = test_client.post(
                '/api/v1/category/1/recipes', headers=self.auth_header,
                data=test_recipe, content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)
            response_data = json.loads(response.data.decode())
            self.assertEqual(len(response_data['recipes']), 1)
            # Duplicate recipe
            response = test_client.post(
                '/api/v1/category/1/recipes', headers=self.auth_header,
                data=test_recipe, content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], 'Recipe already exists!')

    def test_recipes_view_resource_security(self):
        """
        Ensures the resource is projected from unauthorized access
        """

        with self.client as test_client:
            # Ensure no access without Authorization
            response = test_client.get(
                '/api/v1/category/1/recipes', content_type='application/json'
            )
            self.assert401(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], "Please provide an access token!")
            # Ensure no access with invalid authorization
            response = test_client.get(
                '/api/v1/category/1/recipes',
                headers=dict(Authorization="Some98247982hnidutie3rojgnadf"),
                content_type='application/json'
            )
            self.assert401(response, "Wrong reponse code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], 'Invalid token. Login to use this resource!')

    def test_recipes_view(self):
        """
        Ensures user can view recipes for a particular category
        """

        self.set_up()
        with self.client as test_client:
            # Retrieval from a valid category with no recipes yet
            response = test_client.get(
                '/api/v1/category/1/recipes', headers=self.auth_header,
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], 'No recipes added to this category yet!')
            # Add test recipe
            add_recipe_response = test_client.post(
                '/api/v1/category/1/recipes', headers=self.auth_header,
                data=test_recipe, content_type='application/json'
            )
            self.assertEqual(add_recipe_response.status_code, 201)
            # Retrive recipe
            response = test_client.get(
                '/api/v1/category/1/recipes', headers=self.auth_header,
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(len(response_data['recipes']), 1)

            # Attempt retrieval from an invalid category
            response = test_client.get(
                '/api/v1/category/2/recipes', headers=self.auth_header,
                content_type='application/json'
            )
            self.assert400(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], 'Invalid category!')

    def test_single_recipe_retrival_resource_security(self):
        """
        Ensure that this resource is protected from unauthorized use
        """

        # Attempt access with no authorization
        with self.client as test_client:
            response = test_client.get(
                '/api/v1/category/1/recipes/1', content_type='application/json'
            )
            self.assert401(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], 'Please provide an access token!')
            # Attempt access with invalid authorization
            response = test_client.get(
                '/api/v1/category/1/recipes/1', headers=dict(Authorization="gih248h9ehg2iu028"),
                content_type='application/json'
            )
            self.assert401(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(
                response_data['message'],
                'Invalid token. Login to use this resource!'
            )

    def test_single_recipe_retrival(self):
        """
        Ensure that requests to view single recipes are handled accordingly
        """

        # setup
        self.set_up()

        with self.client as test_client:
            # add test recipe
            response = test_client.post(
                '/api/v1/category/1/recipes', headers=self.auth_header,
                data=test_recipe, content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)

            # Retrieve recipe from a valid category with a
            # valid recipe id
            response = test_client.get(
                '/api/v1/category/1/recipes/1', headers=self.auth_header,
                content_type='application/json'
            )
            self.assert200(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(len(response_data['recipes']), 1)

            # retrieve recipe from a valid category with an
            # invalid recipe id
            response = test_client.get(
                '/api/v1/category/1/recipes/2', headers=self.auth_header,
                content_type='application/json'
            )
            self.assert404(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], "Recipe does not exist!")

            # retrieve recipe from an invalid category with a
            # valid/invalid recipe id
            response = test_client.get(
                '/api/v1/category/2/recipes/2', headers=self.auth_header,
                content_type='application/json'
            )
            self.assert404(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], "Category does not exist!")

    def test_single_recipe_update_resource_security(self):
        """
        Ensure that this resource is protected from unauthorized use
        """

        # Attempt access with no authorization
        with self.client as test_client:
            response = test_client.put(
                '/api/v1/category/1/recipes/1',
                data=test_recipe_update, content_type='application/json'
            )
            self.assert401(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], 'Please provide an access token!')

            # Attempt access with invalid authorization
            response = test_client.put(
                '/api/v1/category/1/recipes/1', headers=dict(Authorization="gih248h9ehg2iu028"),
                data=test_recipe_update, content_type='application/json'
            )
            self.assert401(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(
                response_data['message'],
                'Invalid token. Login to use this resource!'
            )

    def test_single_recipe_update(self):
        """
        Ensure that requests to update single recipes are handled accordingly
        """

        # setup
        self.set_up()

        with self.client as test_client:
            # add test recipe
            response = test_client.post(
                '/api/v1/category/1/recipes', headers=self.auth_header,
                data=test_recipe, content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)

            # Update a recipe from a valid category with a
            # valid recipe id with new name and new details
            response = test_client.put(
                '/api/v1/category/1/recipes/1', headers=self.auth_header,
                data=test_recipe_update, content_type='application/json'
            )
            self.assert200(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(
                response_data["message"],
                "Recipe '{}' was successfully updated to '{}'.".format(
                    _clean_name(json.loads(test_recipe)['name']),
                    _clean_name(json.loads(test_recipe_update)['name'])
                )
            )

            # Update a recipe from a valid category with a
            # valid recipe id with same name but new details
            json.loads(test_recipe_update)['description'] = "This is how to prepare..."
            response = test_client.put(
                '/api/v1/category/1/recipes/1', headers=self.auth_header,
                data=test_recipe_update, content_type='application/json'
            )
            self.assert200(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(
                response_data["message"],
                "Recipe '{}' was successfully updated.".format(
                    _clean_name(json.loads(test_recipe_update)['name'])
                )
            )

            # Update recipe from a valid category with an
            # invalid recipe id
            response = test_client.put(
                '/api/v1/category/1/recipes/2', headers=self.auth_header,
                data=test_recipe_update, content_type='application/json'
            )
            self.assert404(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], "Recipe does not exist!")

            # Update recipe from an valid category with a
            # valid/invalid recipe id
            response = test_client.put(
                '/api/v1/category/2/recipes/2', headers=self.auth_header,
                data=test_recipe_update, content_type='application/json'
            )
            self.assert404(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], "Category does not exist!")

    def test_single_recipe_delete_resource_security(self):
        """
        Ensure that this resource is protected from unauthorized use
        """

        # Attempt access with no authorization
        with self.client as test_client:
            response = test_client.delete(
                '/api/v1/category/1/recipes/1', content_type='application/json'
            )
            self.assert401(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], 'Please provide an access token!')
            # Attempt access with invalid authorization
            response = test_client.delete(
                '/api/v1/category/1/recipes/1', headers=dict(Authorization="gih248h9ehg2iu028"),
                content_type='application/json'
            )
            self.assert401(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(
                response_data['message'],
                'Invalid token. Login to use this resource!'
            )

    def test_single_recipe_delete(self):
        """
        Ensure that requests to delete single recipes are handled accordingly
        """

        # setup
        self.set_up()

        with self.client as test_client:
            # add test recipe
            response = test_client.post(
                '/api/v1/category/1/recipes', headers=self.auth_header,
                data=test_recipe, content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)

            # Retrieve recipe from a valid category with a
            # valid recipe id
            response = test_client.get(
                '/api/v1/category/1/recipes/1', headers=self.auth_header,
                content_type='application/json'
            )
            self.assert200(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(len(response_data['recipes']), 1)

            # Delete recipe from a valid category with a
            # valid recipe id
            response = test_client.delete(
                '/api/v1/category/1/recipes/1', headers=self.auth_header,
                content_type='application/json'
            )
            self.assert200(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(
                response_data['message'], 'Recipe chocolate_chip was deleted successfully!'
            )

            # Delete recipe from a valid category with an
            # invalid recipe id
            response = test_client.delete(
                '/api/v1/category/1/recipes/1', headers=self.auth_header,
                content_type='application/json'
            )
            self.assert404(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], "Recipe does not exist!")

            # Delete recipe from an invalid category with a
            # valid/invalid recipe id
            response = test_client.delete(
                '/api/v1/category/2/recipes/2', headers=self.auth_header,
                content_type='application/json'
            )
            self.assert404(response, "Invalid status code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertEqual(response_data['message'], "Category does not exist!")
