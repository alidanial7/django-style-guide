# Celery

Broker: **{{cookiecutter.celery_broker}}**. Tasks stay thin: load IDs → call **services** → map errors.

## Layout

| Piece | Location |
|-------|----------|
| App | `config/celery.py` |
| Settings | `config/settings/celery.py` |
| Task modules | `config/tasks.py` and/or `<app>/tasks.py` |
| Beat | `CELERY_BEAT_SCHEDULE` (empty by default) or django-celery-beat admin |

```bash
celery -A config.celery worker -l INFO
celery -A config.celery beat -l INFO
```

Prod worker/beat: [Docker & production](docker-and-production.md).

## Task style

```python
@shared_task(bind=True, max_retries=3, autoretry_for=(TransientError,), retry_backoff=True)
def publish_post_task(self, *, post_id: int) -> None:
    publish_post(post_id=post_id)  # domain service
```

| Do | Don’t |
|----|-------|
| Pass IDs / small primitives | Pass model instances |
| Call services | Duplicate business ORM in the task |
| Idempotent retries when possible | Assume exactly-once without design |

Settings: broker URL, `django-db` results, soft/hard time limits. Tests: eager mode in `config.django.test`.

Related: [Services](../domain/services.md) · [Logging](logging.md) · [Docker](docker-and-production.md)
