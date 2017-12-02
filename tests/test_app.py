"""Unit testing suite for the app module"""
import time

from uuid import uuid4
from flask_testing import TestCase
from flask import json
from instance.config import app_config
from app import APP
from app.models import db, User, BlacklistToken

from .helpers import register_user

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

class UserNSTestCase(BaseTestCase):
    """This test class contains the tests for the API endpoints"""


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
            register_resp = register_user(self, 'isaac@yummy.io', 'isaac', '123pass321')
            self.assertIn(b'Registered successfully!', register_resp.data)
            self.assertEqual(register_resp.status_code, 201)
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
            register_user(self, 'isaac@yummy.io', 'isaac', '123pass321')
            user = User.query.filter_by(email='isaac@yummy.io').first()
            response = self.client.get(
                '/users/' + user.public_id,
                content_type="application/json"
            )
            self.assertTrue(response.status_code, 200)
            self.assertIn(user.public_id, str(response.data))

class AuthNSTestCase(BaseTestCase):
    """
    This class covers the unit tests for the the user
    auth namespace.
    """
    def test_registration(self):
        """ Test for user registration """
        with self.client:
            response = register_user(self, "isaac@yum.my", "isaac", "123456")
            data = json.loads(response.data.decode())
            self.assertTrue(data['message'] == 'Registered successfully!')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_registered_with_already_registered_user(self):
        """ Test registration with already registered email"""
        user = User(
            email='isaac@yum.my',
            username="isaac",
            password='some_pass'
        )
        db.session.add(user)
        db.session.commit()
        with self.client:
            response = register_user(self, "isaac@yum.my", "Isaac" ,"123456")
            data = json.loads(response.data.decode())
            self.assertTrue(
                data['message'] == 'User already exists. Please Log in instead.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 202)

    def test_login_without_credentials(self):
        """Test login resource without any credentials supplied"""
        with self.client:
            response = self.client.post(
                '/auth/login',
                data = json.dumps(dict()),
                content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assert401
            self.assertTrue(data['message'] == 'Input payload validation failed')

    def test_registered_user_login(self):
        """ Test for login of registered-user login """
        with self.client:
            # user registration
            register_resp = register_user(self, "isaac@yum.my", "isaac", "123456")
            data_register = json.loads(register_resp.data.decode())
            self.assertTrue(
                data_register['message'] == 'Registered successfully!'
            )
            self.assertTrue(register_resp.content_type == 'application/json')
            self.assertEqual(register_resp.status_code, 201)
            # registered user login
            response = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='isaac@yum.my',
                    password='123456'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['message'] == 'Logged in successfully.')
            self.assertTrue(data['access_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 200)

    def test_non_registered_user_login(self):
        """ Test for login of non-registered user """
        with self.client:
            response = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='joe@yum.my',
                    password='123456'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['message'] == 'User does not exist!')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 404)

    def test_registered_user_login_wrong_password(self):
        """ Test for login of registered-user login """
        with self.client:
            # user registration
            register_resp = register_user(self, "isaac@yum.my", "isaac", "123456")
            data_register = json.loads(register_resp.data.decode())
            self.assertTrue(
                data_register['message'] == 'Registered successfully!'
            )
            self.assertTrue(register_resp.content_type == 'application/json')
            self.assertEqual(register_resp.status_code, 201)
            # registered user login with wrong password
            response = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='isaac@yum.my',
                    password='654321'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['message'] == 'Incorrect credentials.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 401)

    def test_valid_logout(self):
        """ Test for logout before token expires """
        with self.client:
            # user registration
            register_resp = register_user(self, "isaac@yum.my", "isaac", "123456")
            data_register = json.loads(register_resp.data.decode())
            self.assertTrue(
                data_register['message'] == 'Registered successfully!')
            self.assertTrue(register_resp.content_type == 'application/json')
            self.assertEqual(register_resp.status_code, 201)
            # user login
            login_resp = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='isaac@yum.my',
                    password='123456'
                )),
                content_type='application/json'
            )
            data_login = json.loads(login_resp.data.decode())
            self.assertTrue(data_login['message'] == 'Logged in successfully.')
            self.assertTrue(data_login['access_token'])
            self.assertTrue(login_resp.content_type == 'application/json')
            self.assertEqual(login_resp.status_code, 200)
            # valid token logout
            response = self.client.post(
                '/auth/logout',
                headers=dict(
                    access_token=json.loads(
                        login_resp.data.decode()
                    )['access_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Logged out successfully.')
            self.assertEqual(response.status_code, 200)

    def test_valid_blacklisted_token_logout(self):
        """ Test for logout after a valid token gets blacklisted """
        with self.client:
            # user registration
            register_resp = register_user(self, "isaac@yum.my", "isaac", "123456")
            data_register = json.loads(register_resp.data.decode())
            self.assertTrue(
                data_register['message'] == 'Registered successfully!')
            self.assertTrue(register_resp.content_type == 'application/json')
            self.assertEqual(register_resp.status_code, 201)
            # user login
            login_resp = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='isaac@yum.my',
                    password='123456'
                )),
                content_type='application/json'
            )
            data_login = json.loads(login_resp.data.decode())
            self.assertTrue(data_login['message'] == 'Logged in successfully.')
            self.assertTrue(data_login['access_token'])
            self.assertTrue(login_resp.content_type == 'application/json')
            self.assertEqual(login_resp.status_code, 200)
            # blacklist a valid token
            blacklist_token = BlacklistToken(
                token=json.loads(login_resp.data.decode())['access_token'])
            db.session.add(blacklist_token)
            db.session.commit()
            # blacklisted valid token logout
            response = self.client.post(
                '/auth/logout',
                headers=dict(
                    access_token=json.loads(
                        login_resp.data.decode()
                    )['access_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, 401)
