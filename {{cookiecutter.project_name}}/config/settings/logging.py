from __future__ import annotations

import logging
from pathlib import Path

from config.env import BASE_DIR, env

_VALID_LEVELS = frozenset({"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"})

_raw_level = env("DJANGO_LOGGING_LEVEL", default="INFO").upper()
if _raw_level not in _VALID_LEVELS:
    logging.getLogger(__name__).warning(
        "Invalid DJANGO_LOGGING_LEVEL=%r; falling back to INFO",
        _raw_level,
    )
    DJANGO_LOGGING_LEVEL = "INFO"
else:
    DJANGO_LOGGING_LEVEL = _raw_level

LOG_TO_FILE = env.bool("LOG_TO_FILE", default=True)
LOG_WHEN = env("LOG_WHEN", default="midnight")
LOG_INTERVAL = env.int("LOG_INTERVAL", default=1)
LOG_BACKUP_COUNT = env.int("LOG_BACKUP_COUNT", default=14)
LOG_SQL = env.bool("LOG_SQL", default=False)

_LOG_ROOT = Path(str(BASE_DIR)) / "logs"
_APP_LOG_FILE = _LOG_ROOT / "app" / "app.log"
_ERROR_LOG_FILE = _LOG_ROOT / "error" / "error.log"


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


if LOG_TO_FILE:
    _ensure_parent(_APP_LOG_FILE)
    _ensure_parent(_ERROR_LOG_FILE)

_CONSOLE_HANDLERS = ["console"]
_FILE_HANDLERS = ["app_file", "error_file"] if LOG_TO_FILE else []
_ROOT_HANDLERS = _CONSOLE_HANDLERS + _FILE_HANDLERS
# django.request ERROR+ → console + app JSON + error JSON (when files on)
_REQUEST_HANDLERS = _CONSOLE_HANDLERS + _FILE_HANDLERS

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id": {
            "()": "config.request_id.RequestIdFilter",
        },
    },
    "formatters": {
        "console": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": "config.logging_formatters.JsonFormatter",
        },
        "sql": {
            "()": "config.logging_formatters.DatabaseFormatter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": DJANGO_LOGGING_LEVEL,
            "formatter": "console",
            "filters": ["request_id"],
        },
        **(
            {
                "app_file": {
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "level": "INFO",
                    "formatter": "json",
                    "filename": str(_APP_LOG_FILE),
                    "when": LOG_WHEN,
                    "interval": LOG_INTERVAL,
                    "backupCount": LOG_BACKUP_COUNT,
                    "encoding": "utf-8",
                    "filters": ["request_id"],
                },
                "error_file": {
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "level": "ERROR",
                    "formatter": "json",
                    "filename": str(_ERROR_LOG_FILE),
                    "when": LOG_WHEN,
                    "interval": LOG_INTERVAL,
                    "backupCount": LOG_BACKUP_COUNT,
                    "encoding": "utf-8",
                    "filters": ["request_id"],
                },
            }
            if LOG_TO_FILE
            else {}
        ),
        **(
            {
                "sql_console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "sql",
                    "filters": ["request_id"],
                },
            }
            if LOG_SQL
            else {}
        ),
    },
    "root": {
        "handlers": _ROOT_HANDLERS,
        "level": DJANGO_LOGGING_LEVEL,
    },
    "loggers": {
        # Propagate to root so app + django framework share one handler set (no duplicates).
        "django": {
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": _REQUEST_HANDLERS,
            "level": "ERROR",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["sql_console"] if LOG_SQL else [],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.utils.autoreload": {
            "level": "INFO",
            "propagate": True,
        },
    },
}
