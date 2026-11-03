import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-local-testing-only")

from .base import *  # noqa

from config.env import env

# Based on https://www.hacksoft.io/blog/optimize-django-build-to-run-faster-on-github-actions

DEBUG = False
ALLOWED_HOSTS = ["*"]
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Quiet logging in tests: console WARNING+, no file handlers, no SQL noise.
LOG_TO_FILE = False
LOG_SQL = False
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "console",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {"level": "WARNING", "propagate": True},
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "django.db.backends": {"handlers": [], "level": "INFO", "propagate": False},
    },
}

{%- if cookiecutter.use_celery == "y" %}
CELERY_BROKER_URL = "memory://"
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
{%- endif %}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Prefer Postgres in CI (GitHub Actions / GitLab CI) or when TEST_DATABASE_URL is set.
# Fall back to SQLite (:memory:) for quick local test runs without external services.
_ci = bool(os.environ.get("GITHUB_WORKFLOW") or os.environ.get("GITLAB_CI"))
_test_db_url = os.environ.get("TEST_DATABASE_URL")
if _test_db_url:
    DATABASES = {"default": env.db("TEST_DATABASE_URL", default=_test_db_url)}
elif _ci and env.str("DATABASE_URL", default=""):
    DATABASES = {"default": env.db("DATABASE_URL")}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
