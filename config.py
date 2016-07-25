# coding:utf-8
"""
    seaside.config
    ~~~~~~~~~~~~~~~~~

    :use absolute path in CELERY_IMPORTS, or celery may come across 'Received unregistered task'
"""
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = 'damn it is hard to guess' or os.environ.get('SECRET_KEY')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    SEASIDE_MAIL_SUBJECT_PREFIX = '[Seaside]'
    SEASIDE_MAIL_SENDER = 'wangzhihao9110@163.com'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SEASIDE_ADMIN = os.environ.get('SEASIDE_ADMIN')
    SEASIDE_POSTS_PER_PAGE = 20
    SEASIDE_POSTS_PER_CARD = 5
    SEASIDE_FOLLOWERS_PER_PAGE = 20
    SEASIDE_COMMENTS_PER_PAGE = 20
    SQLALCHEMY_RECORD_QUERIES = True
    SEASIDE_DB_QUERY_TIMEOUT = 0.5
    SEASIDE_SLOW_DB_QUERY_TIME = 0.5
    SSL_DISABLE = True
    MAX_SEARCH_RESULTS = 50
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_IMPORTS = ('seaside.longtasks',)


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    WHOOSH_BASE = os.path.join(basedir, 'search-dev.db')


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WHOOSH_BASE = os.path.join(basedir, 'search-test.db')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    WHOOSH_BASE = os.path.join(basedir, 'search.db')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.SEASIDE_MAIL_SENDER,
            toaddrs=[cls.SEASIDE_ADMIN],
            subject=cls.SEASIDE_MAIL_SUBJECT_PREFIX + 'Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class HerokuConfig(ProductionConfig):
    SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))
    DEBUG = True

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # handle proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,
    'default': DevelopmentConfig,
}

