Seaside

This repository contains the source code for my website [Seaside] based on Flask.

To run this web app, install all extensions listed in the requirement file as well as redis-server, virtual env is highly recommended.
Then 3 terminals are required:

    No.1 for redis, $redis-server /usr/local/etc/redis.conf

    No.2 for celery, (venv)$celery -A manage.celery worker --loglevel=info

    No.3 for app, (venv)$python manage.py runserver

Note that you need to set environment variable 'SEASIDE_MAIL_SENDER', 'MAIL_USERNAME', 'MAIL_PASSWORD' in both terminal
2 & 3 to send mails.

This prj is built according ot M(models) V(views) T(templates) model:

    Models are based on Flask-SQLAlchemy, all complex logic implemented here;

    Templates are based on Jinja2, and lots of js making UI easy to use;

    Celery with redis are used to schedule high time cost tasks such as sending mails.


Have fun :)