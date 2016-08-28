import unittest
from app import create_app, db
from app.models import User, Role
from flask import url_for
import re


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @unittest.skip
    def test_register_and_login(self):
        # registration
        response = self.client.post(url_for('auth.login'), data={
            'email': 'john@example.com',
            'username': 'john',
            'password': 'catdog',
            'password2': 'catdog',
            'submit': '注册'
        })
        self.assertTrue(response.status_code == 302)

        # login
        # response = self.client.post(url_for('auth.login'), data={
        #     'email': 'john@example.com',
        #     'password': 'cat',
        # }, follow_redirects=True)
        # data = response.get_data(as_text=True)
        # self.assertTrue(re.search('Hello,\s+john!', data))

        # send token
        user = User.query.filter_by(email='john@example.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get(url_for('auth.confirm', token=token), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue('You have confirmed your account' in data)

        # logout
        response = self.client.get(url_for('auth.logout'),
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue('You have been logged out' in data)
