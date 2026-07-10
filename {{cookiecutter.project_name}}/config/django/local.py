from .base import *  # noqa
{% if cookiecutter.use_celery == "y" %}

CELERY_BROKER_BACKEND = "memory"
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
{% endif %}

DEBUG = True

# Local development: allow any origin unless overridden in .env.
CORS_ALLOW_ALL_ORIGINS = True
