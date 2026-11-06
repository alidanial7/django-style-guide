#!/bin/sh

echo "Apply database migrations"
python manage.py migrate

echo "Seed local demo data (idempotent)"
python manage.py seed_demo_data

{%- if cookiecutter.use_celery == "y" %}
echo "Starting Celery worker"
celery -A config.celery worker -l info --without-gossip --without-mingle --without-heartbeat > celery.log 2>&1 &
{%- endif %}

echo "Starting Django runserver"
python manage.py runserver 0.0.0.0:8000
