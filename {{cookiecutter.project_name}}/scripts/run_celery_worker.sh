#!/bin/sh
set -e

echo "--> Starting Celery worker (concurrency=4, queues=default,celery)..."
exec celery -A config worker -Q default,celery --concurrency=4 --loglevel=INFO -n default_worker@%h
