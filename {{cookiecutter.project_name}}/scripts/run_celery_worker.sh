#!/bin/sh
set -e

echo "--> Starting Celery worker (concurrency=4, queue=default)..."
exec celery -A config worker -Q default --concurrency=4 --loglevel=INFO -n default_worker@%h
