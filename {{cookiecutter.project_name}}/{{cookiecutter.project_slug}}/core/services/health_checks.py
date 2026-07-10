from __future__ import annotations

import socket
import time
from typing import Any
from urllib.parse import urlparse

import django
from django.conf import settings
from django.core.cache import cache
from django.db import connection

from config.env import env


def _latency_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)


def _aggregate_status(checks: dict[str, dict[str, Any]]) -> str:
    if any(component.get("status") == "error" for component in checks.values()):
        return "error"
    return "ok"


def check_django() -> dict[str, Any]:
    start = time.perf_counter()
    return {
        "status": "ok",
        "latency_ms": _latency_ms(start),
        "version": django.get_version(),
        "settings_module": settings.SETTINGS_MODULE,
        "debug": settings.DEBUG,
    }


def check_database() -> dict[str, Any]:
    start = time.perf_counter()
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return {
            "status": "ok",
            "latency_ms": _latency_ms(start),
            "engine": settings.DATABASES["default"]["ENGINE"],
            "name": settings.DATABASES["default"].get("NAME"),
        }
    except Exception as exc:
        return {
            "status": "error",
            "latency_ms": _latency_ms(start),
            "detail": str(exc),
        }


{% if cookiecutter.use_redis == "y" -%}
def check_redis() -> dict[str, Any]:
    start = time.perf_counter()
    probe_key = "healthcheck:probe"
    try:
        cache.set(probe_key, "ok", timeout=10)
        if cache.get(probe_key) != "ok":
            raise RuntimeError("cache read/write mismatch")
        return {
            "status": "ok",
            "latency_ms": _latency_ms(start),
            "backend": settings.CACHES["default"]["BACKEND"],
            "location": settings.CACHES["default"].get("LOCATION"),
        }
    except Exception as exc:
        return {
            "status": "error",
            "latency_ms": _latency_ms(start),
            "detail": str(exc),
        }


{% endif -%}{% if cookiecutter.use_rabbitmq == "y" -%}
def _broker_url() -> str:
    return env(
        "RABBITMQ_URL",
        default=env("CELERY_BROKER_URL", default="amqp://guest:guest@localhost:5672//"),
    )


def check_rabbitmq() -> dict[str, Any]:
    start = time.perf_counter()
    broker_url = _broker_url()
    try:
        normalized = broker_url.replace("amqp://", "http://", 1)
        parsed = urlparse(normalized)
        host = parsed.hostname or "localhost"
        port = parsed.port or 5672
        with socket.create_connection((host, port), timeout=2.0):
            pass
        return {
            "status": "ok",
            "latency_ms": _latency_ms(start),
            "host": host,
            "port": port,
        }
    except OSError as exc:
        return {
            "status": "error",
            "latency_ms": _latency_ms(start),
            "detail": str(exc),
            "broker_url": broker_url,
        }


{% endif -%}{% if cookiecutter.use_celery == "y" -%}
def check_celery() -> dict[str, Any]:
    start = time.perf_counter()
    if getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False):
        return {
            "status": "ok",
            "latency_ms": _latency_ms(start),
            "detail": "tasks run eagerly in this environment (worker not required)",
        }

    try:
        from config.celery import app

        ping = app.control.inspect(timeout=1.0).ping() or {}
        if not ping:
            return {
                "status": "error",
                "latency_ms": _latency_ms(start),
                "detail": "no celery workers responded",
            }
        return {
            "status": "ok",
            "latency_ms": _latency_ms(start),
            "workers": sorted(ping.keys()),
        }
    except Exception as exc:
        return {
            "status": "error",
            "latency_ms": _latency_ms(start),
            "detail": str(exc),
        }


{% endif -%}
def run_health_checks() -> dict[str, Any]:
    checks: dict[str, dict[str, Any]] = {
        "django": check_django(),
        "database": check_database(),
    }

{% if cookiecutter.use_redis == "y" %}    checks["redis"] = check_redis()
{% endif %}
{% if cookiecutter.use_rabbitmq == "y" %}    checks["rabbitmq"] = check_rabbitmq()
{% endif %}
{% if cookiecutter.use_celery == "y" %}    checks["celery"] = check_celery()
{% endif %}
    return {
        "status": _aggregate_status(checks),
        "checks": checks,
    }
