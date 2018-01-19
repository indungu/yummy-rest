"""Test suite for APP initialization"""
import json
from flask_testing import TestCase
from app import APP
from instance.config import app_config

class AppInitTestCase(TestCase):
    """
    A class testing APP init configurations
    """
    def create_app(self):
        """creates an app for testing"""
        APP.config.from_object(app_config['testing'])
        return APP

    def test_redirects_root_to_docs(self):
        """
        Tests that the root url redirects to API docs
        """
        with self.client as client:
            response = client.get('/')
            # assert that the status code is a redirect
            self.assertEqual(response.status_code, 302)

    def test_404_error_is_json(self):
        """
        Tests that all 404 errors are returned in JSON format
        """
        with self.client as client:
            response = client.get(
                "/bad/url", content_type="application/json"
            )
            response_payload = json.loads(response.data)
            # Assert 404 status and associated message
            self.assertEqual(response.status_code, 404)
            self.assertEqual(
                response_payload['message'],
                "The requested URL was not found on the server. " + \
                "If you entered the URL manually please check your spelling and try again."
            )
