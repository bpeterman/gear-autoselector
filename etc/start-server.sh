#!/bin/bash -e

if [ "$DJANGO_DEBUG" == 'true' ];
then
    echo -e "starting local server"
    exec python manage.py runserver 0.0.0.0:8000
else
    exec -e "starting gunicorn"
    exec gunicorn -b 0.0.0.0:8000 gearselector.wsgi
fi