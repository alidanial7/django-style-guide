# ⏱️ Celery & background tasks

{%- if cookiecutter.use_celery == "y" %}
> This project was generated **with Celery**. Broker: **{{cookiecutter.celery_broker}}**.
>
> Keep tasks **thin**: validate/load IDs in the task, call **services** for business rules, map errors deliberately.

---

## 🎯 Layout

| Piece | Location |
|-------|----------|
| Celery app | `config/celery.py` |
| Settings | `config/settings/celery.py` |
| Sample task | `config/tasks.py` (`notify_customers`) |
| Autodiscover | Installed apps’ `tasks.py` modules |

```bash
# local (devserver may start a worker when enabled)
celery -A config.celery worker -l INFO
celery -A config.celery beat -l INFO
```

Production Compose runs worker + beat containers — see [Docker & production](docker-and-production.md).

---

## ✅ Task style

```python
import logging
from celery import shared_task

from {{cookiecutter.project_slug}}.blogs.services import publish_post

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, autoretry_for=(TransientError,), retry_backoff=True)
def publish_post_task(self, *, post_id: int) -> None:
    logger.info("publish_post_task post_id=%s", post_id)
    publish_post(post_id=post_id)  # domain service
```

| ✅ Do | ❌ Don’t |
|-------|---------|
| Pass IDs / small primitives | Pass whole model instances |
| Call services for writes | Duplicate ORM business rules in the task |
| `logger.info` / `exception` | `print` |
| Idempotent retries when possible | Assume exactly-once without design |
| Soft/hard time limits (settings) | Unbounded tasks |

---

## ⚙️ Settings knobs

From `config/settings/celery.py`:

- `CELERY_BROKER_URL` (env)
- `CELERY_RESULT_BACKEND = "django-db"`
- `CELERY_TASK_SOFT_TIME_LIMIT` / `CELERY_TASK_TIME_LIMIT`
- `CELERY_BEAT_SCHEDULE` — replace the sample `notify_customers` beat before production

Tests use eager mode (`CELERY_TASK_ALWAYS_EAGER`) in `config.django.test`.

---

## 🔗 Related

| Doc | Why |
|-----|-----|
| [Services](services.md) | Business writes |
| [Logging](logging.md) | How to log inside tasks |
| [Enterprise extensions](enterprise-extensions.md) | Outbox pattern if you need reliable publish |
| [Docker & production](docker-and-production.md) | Worker containers |

{%- else %}
> Celery was **not** enabled at generation (`use_celery=n`).
>
> To add it later: introduce broker (Redis/RabbitMQ), `config/celery.py`, worker processes, and follow the task style above (thin tasks → services). Prefer regenerating with `use_celery=y` if you are early in the project.
{%- endif %}
