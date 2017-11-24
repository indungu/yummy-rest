"""Unit testing suite for the app module"""
from uuid import uuid4
from flask_testing import TestCase
from flask import json
from instance.config import app_config
from app import APP
from app.models import db, User

class BaseTestCase(TestCase):
    """This class is the base of all test cases"""
    def create_app(self):
        """creates an app for testing"""
        APP.config.from_object(app_config['testing'])
        return APP
    
    def setUp(self):
        """Set up tests"""
        db.create_all()
        db.session.commit()
        
    def tearDown(self):
        """Tear down"""
        # bind the app to the current context
        db.session.remove()
        db.drop_all()

class RoutesTestCase(BaseTestCase):
    """This test class contains the tests for the API endpoints"""


    def register_user(self, email, username, password):
        """Registers a test user"""
        return self.client.post('/auth/register',
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
        with self.client:
            response = self.client.get('/users', follow_redirects=True, content_type='application/json')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'No user(s) added!', response.data)
            # add a test user
            resp_register = self.register_user('isaac@yummy.io', 'isaac', '123pass321')
            self.assertIn(b'New User created!', resp_register.data)
            self.assertEqual(resp_register.status_code, 201)
            # Ensure that added users are added
            response = self.client.get('/users', follow_redirects=True, content_type='application/json')
            self.assertIn(b'users', response.data)

    def test_single_user_retrival(self):
        """
        This tests whether a single user can be retrieved
        """
        # retrieve an none existed user
        public_id = str(uuid4())
        response = self.client.get(
            '/users/' + public_id,
            content_type="application/json"
        )
        with self.client:
            response_data = json.loads(response.data.decode())
            self.assertTrue(response.status_code, 204)
            # add test user
            self.register_user('isaac@yummy.io', 'isaac', '123pass321')
            user = User.query.filter_by(email='isaac@yummy.io').first()
            response = self.client.get(
                '/users/' + user.public_id,
                content_type="application/json"
            )
            self.assertTrue(response.status_code, 200)
            self.assertIn(user.public_id, str(response.data))
