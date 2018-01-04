"""Unit testing suite for the app module"""
from flask_testing import TestCase
from flask import json
from instance.config import app_config
from app import APP
from app.models import db, User, BlacklistToken

from .helpers import register_user, user_details_inv_email,\
                     user_details_inv_username, user_details_inv_username_2

# pylint: disable=C0103
# pylint: disable=E1101

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

class AuthNSTestCase(BaseTestCase):
    """
    This class covers the unit tests for the the user
    auth namespace.
    """
    def test_registration(self):
        """ Test for user registration """
        with self.client:
            response = register_user(self)
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
            response = register_user(self)
            data = json.loads(response.data.decode())
            self.assertTrue(
                data['message'] == 'User already exists. Please Log in instead.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_registration_with_invalid_email(self):
        """ Test for user registration """
        with self.client:
            response = register_user(self, user_data=user_details_inv_email)
            data = json.loads(response.data.decode())
            self.assertTrue(
                data['message'] == 'You provided some invalid details.'
            )
            self.assertTrue(
                'email' in data['errors']
            )
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 422)

    def test_registration_with_invalid_username(self):
        """ Test for user registration """
        with self.client:
            # When the username has special characters
            response = register_user(self, user_data=user_details_inv_username)
            data = json.loads(response.data.decode())
            self.assertTrue(
                data['message'] == 'You provided some invalid details.'
            )
            errors = data['errors']
            self.assertTrue(
                'username' in errors
            )
            self.assertEqual(
                errors['username'][0], 'Username should only contain letters and numbers.'
            )
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 422)

            # When the username is of invalid length
            response = register_user(self, user_data=user_details_inv_username_2)
            data = json.loads(response.data.decode())
            self.assertTrue(
                data['message'] == 'You provided some invalid details.'
            )
            errors = data['errors']
            self.assertTrue(
                'username' in errors
            )
            self.assertEqual(
                errors['username'][0], 'Username should be 3 or more characters long.'
            )
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 422)

    def test_login_without_credentials(self):
        """Test login resource without any credentials supplied"""
        with self.client:
            response = self.client.post(
                '/auth/login',
                data=json.dumps(dict()),
                content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assert400(response, "Invalid response code: " + str(response.status_code))
            self.assertTrue(data['message'] == 'Input payload validation failed')

    def test_registered_user_login(self):
        """ Test for login of registered-user login """
        with self.client:
            # user registration
            register_resp = register_user(self)
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
                    password='1234509876'
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
                    password='1234509876'
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
            register_resp = register_user(self)
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
            register_resp = register_user(self)
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
                    password='1234509876'
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
                    Authorization=json.loads(
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
            register_resp = register_user(self)
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
                    password='1234509876'
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
                    Authorization=json.loads(
                        login_resp.data.decode()
                    )['access_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_user_password_reset(self):
        """
        This test ensures that refistered users can reset their
        current password
        """
        with self.client:
            # user registration
            register_user(self)
            # login user
            self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='isaac@yum.my',
                    password='1234509876'
                )),
                content_type='application/json'
            )
            # User public ID
            user = User.query.filter_by(email="isaac@yum.my").first()
            public_id = user.public_id

            # ensure that user can reset thier password granted
            # they provide the correct public id and current_password
            response = self.client.post(
                '/auth/reset-password',
                data=json.dumps(dict(
                    public_id=public_id,
                    current_password='1234509876',
                    new_password='12345678',
                )),
                content_type='application/json'
            )
            self.assert200(response, "Invalid response code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertTrue(response_data['status'] == "Success!")
            self.assertTrue(response_data['message'] == "Password reset successfully!")

            # ensure that user cannot reset thier password if/when
            # they provide the incorrect current_password
            response = self.client.post(
                '/auth/reset-password',
                data=json.dumps(dict(
                    public_id=public_id,
                    current_password='1234509876',
                    new_password='12345678',
                )),
                content_type='application/json'
            )
            self.assert401(response, "Invalid response code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertTrue(response_data['status'] == "Fail!")
            self.assertTrue(response_data['message'] == "Wrong current password. Try again.")

            # ensure that user cannot reset thier password if/when
            # they provide the incorrect public_id
            response = self.client.post(
                '/auth/reset-password',
                data=json.dumps(dict(
                    public_id="public_id",
                    current_password='1234509876',
                    new_password='12345678',
                )),
                content_type='application/json'
            )
            self.assert403(response, "Invalid response code: " + str(response.status_code))
            response_data = json.loads(response.data.decode())
            self.assertTrue(response_data['status'] == "Fail!")
            self.assertEqual(
                response_data['message'], "User doesn't exist, check the Public ID provided!"
            )
