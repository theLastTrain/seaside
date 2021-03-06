#!/usr/bin/env python
"""
    seaside.manage
    ~~~~~~~~~~~~~~~~~

    Starts web app

    :three terminals are needed: 1 for redis-server, 1 for celery, and the last for web app

"""
import os
import sys
from app import create_app, db, make_celery
from app.models import User, Role, Post, Follow, Comment, Like, TagTree, Tag, Notify, UserNotify, Subscribe
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

# Append parent dir to path
sys.path.append('..')

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)
celery = make_celery(app)


def make_shell_context():
    """
        this function works as: >>>from *** import app, db, User, Role
    """
    return dict(app=app, db=db, User=User, Role=Role, Post=Post, Follow=Follow, Comment=Comment,
                Like=Like, TagTree=TagTree, Tag=Tag, Notify=Notify, UserNotify=UserNotify, Subscribe=Subscribe)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'temp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def profile(length=25, profile_dir=None):
    """ start the application under the code profiler. """
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    app.run()


@manager.command
def deploy():
    """Run deployment tasks"""
    from flask.ext.migrate import upgrade
    from app.models import Role, User
    # migrate data base to newest edtion
    upgrade()
    # create user roles
    Role.insert_roles()
    User.add_self_follows()


if __name__ == '__main__':
    manager.run()


