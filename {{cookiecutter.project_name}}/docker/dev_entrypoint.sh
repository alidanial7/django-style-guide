#!/bin/sh

echo "Apply database migrations"
python manage.py migrate

echo "Creating superuser"
python manage.py shell -c "
from django.contrib.auth import get_user_model

User = get_user_model()
{%- if cookiecutter.use_jwt == "y" %}
if not User.objects.filter(email='admin@example.com').exists():
    User.objects.create_superuser('admin@example.com', 'admin')
    print('Superuser created: admin@example.com / admin')
else:
    print('Superuser already exists.')
{%- else %}
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created: admin / admin')
else:
    print('Superuser already exists.')
{%- endif %}
"

{%- if cookiecutter.use_celery == "y" %}
echo "Starting Celery worker"
celery -A config.celery worker -l info --without-gossip --without-mingle --without-heartbeat > celery.log 2>&1 &
{%- endif %}

echo "Starting Django runserver"
python manage.py runserver 0.0.0.0:8000
