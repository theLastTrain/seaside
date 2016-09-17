import unittest
from unittest import skip
import time
from datetime import datetime
from app import create_app, db
from app.models import User, Notify, UserNotify, NotifyType, TargetType, ActionType


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_send_message(self):
        cat = User(username='cat')
        dog = User(username='dog')
        cat.send_message(dog, 'mew')
        self.assertTrue(cat.sent_notifies.first() == dog.messages.first())
