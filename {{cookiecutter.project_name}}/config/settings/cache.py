{%- if cookiecutter.use_redis == "y" -%}
from config.env import env

# Redis DB segregation (defaults):
#   /0 = Django cache
#   /1 = reserved (sessions / throttle / OTP — wire as needed)
#   /2 = Channels (when WebSockets enabled)
#   /3 = Celery broker fallback (when Celery uses Redis)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_LOCATION", default="redis://localhost:6379/0"),
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
