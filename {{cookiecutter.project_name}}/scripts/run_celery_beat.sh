#!/bin/sh
set -e

echo "--> Starting Celery beat scheduler..."
exec celery -A config beat --loglevel=INFO
