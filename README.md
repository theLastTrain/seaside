Seaside

This repository contains the source code for my website [Seaside] based on Flask.

To run this web app, install all extensions listed in the requirement file as well as redis-server, virtual env is highly recommended.
Then 4 steps are to followed:

    1.set environment variables 'SEASIDE_MAIL_SENDER', 'MAIL_USERNAME', 'MAIL_PASSWORD'

    2. $redis-server /usr/local/etc/redis.conf &

    3. (venv)$celery -A manage.celery worker --loglevel=info &

    4. (venv)$python manage.py runserver

This prj is built according ot M(models) V(views) T(templates) model:

    Models are based on Flask-SQLAlchemy, all complex logic implemented here;

    Templates are based on Jinja2, and lots of js making UI easy to use;

    Celery with redis are used to schedule high time cost tasks such as mail sending.


Have fun :)