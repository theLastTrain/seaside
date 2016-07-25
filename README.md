Seaside

This repository contains the source code for my blog site [Seaside] based on Flask.

To fully run this web app, you need to install all extensions listed in the requirement file as well as redis-server.
Three terminals are required:
    1 for redis, $redis-server /usr/local/etc/redis.conf
    2 for celery, $celery -A manage.celery worker --loglevel=info
      High time consumption tasks are scheduled by Celery such as sending mail, check them out in longtasks.py;
    3 for app, $python manage.py runserver
then enjoy yourself.

This prj consists of three parts M(models) V(services) & T(templates)
    . Models are based by Flask-SQLAlchemy, all complex logic implemented here;
    . Services handle requests and returns query results of db;
    . Templates based on Jinja2, and some JS scripts to make the pages more readable and easy to use
