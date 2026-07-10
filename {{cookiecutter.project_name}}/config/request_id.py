from __future__ import annotations

import logging
import uuid
from contextvars import ContextVar

_request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

REQUEST_ID_HEADER = "X-Request-ID"


def get_request_id() -> str | None:
    return _request_id_var.get()


class RequestIdFilter(logging.Filter):
    """Attach request_id from contextvars onto log records when present."""

    def filter(self, record: logging.LogRecord) -> bool:
        request_id = _request_id_var.get()
        if request_id:
            record.request_id = request_id
        return True


class RequestIdMiddleware:
    """
    Ensure every request has an ID:
    - reuse inbound X-Request-ID when provided
    - otherwise generate uuid4
    - expose on request.request_id, response header, and logging context
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        incoming = request.headers.get(REQUEST_ID_HEADER)
        request_id = incoming.strip() if incoming else str(uuid.uuid4())
        request.request_id = request_id
        token = _request_id_var.set(request_id)
        try:
            response = self.get_response(request)
            response[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            _request_id_var.reset(token)
