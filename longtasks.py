"""
    seaside.longtasks
    ~~~~~~~~~~~~~~~~~

    Holds all celery tasks

    :use absolute import to avid 'beyond top-level relative import' error.
    :celery instance is inited in seaside.manage right after 'app'
"""
from seaside.manage import celery, app
from app import mail


@celery.task
def send_async_email(msg):
    with app.app_context():
        mail.send(msg)
