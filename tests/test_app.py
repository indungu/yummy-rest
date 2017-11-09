"""Unit testing suite for the app module"""

from unittest import TestCase

from app import APP

class RoutesTestCase(TestCase):
    """This test class contains the tests for the API endpoints"""

    def setUp(self):
        """Set up tests"""
        self.test_api = APP.test_client()

    def test_index_route(self):
        """
        This test whether the index route can be reached
        and the response upon successful reach is a JSON welcome
        object
        """
        response = self.test_api.get('/')
        self.assertEqual(response.status_code, 200)
