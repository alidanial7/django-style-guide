#!/bin/sh
set -eu

echo "--> Waiting for db to be ready"
./wait-for-it.sh db:5432

echo "Ensure media directory exists"
mkdir -p /app/media /app/staticfiles

echo "Apply database migrations"
python manage.py migrate --noinput

echo "Collect static files"
python manage.py collectstatic --noinput

echo "--> Starting web process"
{%- if cookiecutter.use_asgi == "y" %}
exec uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --workers 2 --proxy-headers --forwarded-allow-ips='*'
{%- else %}
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 60 \
    --graceful-timeout 30 \
    --access-logfile - \
    --error-logfile -
{%- endif %}
