{%- if cookiecutter.use_redis == "y" -%}
from config.env import env

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_LOCATION", default="redis://localhost:6379"),
    }
}
{%- else -%}
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
{%- endif %}

CACHE_TTL = 60 * 15
