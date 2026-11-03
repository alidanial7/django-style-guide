{%- if cookiecutter.use_celery == "y" %}
from .celery import celery as celery_app

__all__ = ("celery_app",)
{%- endif %}
