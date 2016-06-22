import unittest
from unittest import skip
import time
from datetime import datetime
from app import create_app, db
from app.models import User, Role, AnonymousUser, Permission, Follow


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

    @skip
    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    @skip
    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    @skip
    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    @skip
    def test_password_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    @skip
    def test_valid_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    @skip
    def test_invalid_confirmation_token(self):
        u1 = User(password='cat')
        u2 = User(password='dog')
        db.session.add_all([u1, u2])
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    @skip
    def test_expired_confirmation_token(self):
        u = User(password="cat")
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))

    @skip
    def test_roles_and_permission(self):
        Role.insert_roles()
        u = User(email='john@example.com', password='cat')
        self.assertTrue((u.can(Permission.WRITE_ARTICLES)))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

    @skip
    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))

    def test_follows(self):
        # u1 = User(email='tansiyu@example.com', password='cat')
        # u2 = User(email='wangzhihao@example.com', password='dog')
        # db.session.add(u1)
        # db.session.add(u2)
        # self.assertFalse(u1.is_following(u2))
        # self.assertFalse(u1.is_followed_by(u2))
        # timestamp_before = datetime.utcnow()
        # u1.follow(u2)
        # db.session.add(u1)
        # db.session.commit()
        # timestamp_after = datetime.utcnow()
        # self.assertTrue(u1.is_following(u2))
        # self.assertFalse(u1.is_followed_by(u2))
        # self.assertTrue(u2.is_followed_by(u1))
        # self.assertTrue(u1.followed.count() == 1)
        # self.assertTrue(u2.followers.count() == 1)
        # f = u1.followed.all()[-1]
        # self.assertTrue(f.followed == u2)
        # self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
        # f = u2.followers.all()[-1]
        # self.assertTrue(f.follower == u1)
        # u1.unfollow(u2)
        # db.session.add(u1)
        # db.session.commit()
        # self.assertTrue(u1.followed.count() == 0)
        # self.assertTrue(u2.followers.count() == 0)
        # self.assertTrue(Follow.query.count() == 0)
        # u2.follow(u1)
        # db.session.add(u1)
        # db.session.add(u2)
        # db.session.commit()
        # db.session.delete(u2)
        # db.session.commit()
        # self.assertTrue(Follow.query.count() == 0)
        u1 = User(email='john@example.com', password='cat')
        u2 = User(email='susan@example.org', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        timestamp_before = datetime.utcnow()
        u1.follow(u2)
        db.session.add(u1)
        db.session.commit()
        timestamp_after = datetime.utcnow()
        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        self.assertTrue(u2.is_followed_by(u1))
        self.assertTrue(u1.followed.count() == 2)
        self.assertTrue(u2.followers.count() == 2)
        f = u1.followed.all()[-1]
        self.assertTrue(f.followed == u2)
        self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
        f = u2.followers.all()[-1]
        self.assertTrue(f.follower == u1)
        u1.unfollow(u2)
        db.session.add(u1)
        db.session.commit()
        self.assertTrue(u1.followed.count() == 1)
        self.assertTrue(u2.followers.count() == 1)
        self.assertTrue(Follow.query.count() == 2)
        u2.follow(u1)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        db.session.delete(u2)
        db.session.commit()
        self.assertTrue(Follow.query.count() == 1)
