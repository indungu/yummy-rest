"""Unit testing suite for the app module"""

from unittest import TestCase
from flask import json
from app import APP
from app.models import db, User

class RoutesTestCase(TestCase):
    """This test class contains the tests for the API endpoints"""

    def setUp(self):
        """Set up tests"""
        APP.config['SQLALCHEMY_DATABSE_URI'] = 'postgres://indungu:password@localhost:5432/test_db'
        self.test_api = APP.test_client()

        db.create_all()
        
    def tearDown(self):
        """Tear down"""
        # bind the app to the current context
        db.drop_all()

    def test_user_retrieval(self):
        """
        This test whether the index route can be reached
        and the response upon successful reach is a JSON welcome
        object
        """
        # When retieving users from the database 
        # Ensure that if the database has no users
        response = self.test_api.get('/users', follow_redirects=True, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No user(s) added!', response.data)
        
