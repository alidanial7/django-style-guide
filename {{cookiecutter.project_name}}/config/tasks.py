"""Celery task modules.

Keep tasks thin: load IDs → call domain services → map errors.
Add `@shared_task` functions in this file or per-app `tasks.py` modules.
"""
