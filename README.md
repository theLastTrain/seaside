Seaside

This repository contains the source code for my blog site [Seaside] based on Flask.

To run this web app, virtual env is highly recommended.

Install all extensions listed in the requirement file as well as redis-server,
then 3 terminals are required:

    1 for redis, $redis-server /usr/local/etc/redis.conf

    2 for celery, (venv)$celery -A manage.celery worker --loglevel=info

    3 for app, (venv)$python manage.py runserver

Note that you need to set environment variable 'SEASIDE_MAIL_SENDER', 'MAIL_USERNAME', 'MAIL_PASSWORD' in both terminal
2 & 3 to send a mail.

This prj consists of three parts M(models) V(services) & T(templates)

    . Models are based by Flask-SQLAlchemy, all complex logic implemented here;

    . Services handle requests and returns query results of db;

    . Templates based on Jinja2, and some JS scripts to make the pages more readable and easy to use

    Celery with redis are used to schedule high time cost tasks such as sending mails.

Have fun :)