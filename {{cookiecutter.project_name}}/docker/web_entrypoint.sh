#!/bin/sh

echo "--> Waiting for db to be ready"
./wait-for-it.sh db:5432

echo "Ensure media directory exists"
mkdir -p /app/media

echo "Apply database migrations"
python manage.py migrate
python manage.py collectstatic --clear --noinput
python manage.py collectstatic --noinput

echo "--> Starting web process"
gunicorn config.wsgi:application -b 0.0.0.0:8000
