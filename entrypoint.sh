#!/bin/sh

# Django setup
python manage.py migrate --no-input

python manage.py runserver 0.0.0.0:8000

# Start Gunicorn
# python manage.py collectstatic --no-input --clear
# gunicorn mofidtrip.wsgi:application --bind 0.0.0.0:8000
