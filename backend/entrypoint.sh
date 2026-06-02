#!/bin/sh
set -e

python manage.py migrate --noinput

exec gunicorn --bind "0.0.0.0:${PORT:-10000}" smart_property_finder.wsgi:application
