"""Unit testing suite for the app module"""
from uuid import uuid4
from unittest import TestCase
from flask import json
from app import APP
from app.models import db, User

class RoutesTestCase(TestCase):
    """This test class contains the tests for the API endpoints"""

    def setUp(self):
        """Set up tests"""
        APP.config['SQLALCHEMY_DATABSE_URI'] = 'postgresql://localhost/test_db'
        self.test_api = APP.test_client()

        db.create_all()
        db.session.commit()
        
    def tearDown(self):
        """Tear down"""
        # bind the app to the current context
        db.session.remove()
        db.drop_all()

    def register_user(self, email, username, password):
        """Registers a test user"""
        return self.test_api.post('/auth/register',
                                  data=json.dumps(dict(
                                      email=email,
                                      username=username,
                                      password=password
                                  )), content_type="application/json"
                                 )

    def test_users_retrieval(self):
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
        # add a test user
        resp_register = self.register_user('isaac@yummy.io', 'isaac', '123pass321')
        self.assertIn(b'New User created!', resp_register.data)
        self.assertEqual(resp_register.status_code, 201)
        # Ensure that added users are added
        response = self.test_api.get('/users', follow_redirects=True, content_type='application/json')
        self.assertIn(b'users', response.data)

    def test_single_user_retrival(self):
        """
        This tests whether a single user can be retrieved
        """
        # retrieve an none existed user
        public_id = str(uuid4())
        response = self.test_api.get(
            '/users/' + public_id,
            content_type="application/json"
        )
        response_data = json.loads(response.data.decode())
        self.assertTrue(response.status_code, 204)
        # add test user
        self.register_user('isaac@yummy.io', 'isaac', '123pass321')
        user = User.query.filter_by(email='isaac@yummy.io').first()
        response = self.test_api.get(
            '/users/' + user.public_id,
            content_type="application/json"
        )
        self.assertTrue(response.status_code, 200)
        self.assertIn(user.public_id, str(response.data))
