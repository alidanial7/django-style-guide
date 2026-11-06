from .base import *  # noqa
{% if cookiecutter.use_celery == "y" %}
from config.env import env

# Set to True in .env if you want to execute tasks synchronously without running a worker
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)
CELERY_TASK_EAGER_PROPAGATES = env.bool("CELERY_TASK_EAGER_PROPAGATES", default=False)
{% endif %}

DEBUG = True

# Local development: allow any origin unless overridden in .env.
CORS_ALLOW_ALL_ORIGINS = True
