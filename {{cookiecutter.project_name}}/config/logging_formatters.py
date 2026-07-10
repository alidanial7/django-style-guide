from __future__ import annotations

import json
import logging
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """One JSON object per line for file aggregation (Loki/ELK/Datadog-friendly)."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
            "funcName": record.funcName,
        }
        request_id = getattr(record, "request_id", None)
        if request_id:
            payload["request_id"] = request_id
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info).strip()
        return json.dumps(payload, ensure_ascii=False)


class DatabaseFormatter(logging.Formatter):
    """Readable SQL lines when LOG_SQL=true (django.db.backends)."""

    def format(self, record: logging.LogRecord) -> str:
        duration = getattr(record, "duration", None)
        sql = getattr(record, "sql", None) or record.getMessage()
        if duration is not None:
            return f"({duration:.3f}s) {sql}"
        return str(sql)
