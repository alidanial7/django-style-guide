from __future__ import annotations

import logging

from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error
from rest_framework.views import exception_handler

from {{cookiecutter.project_slug}}.common.errors.codes import ErrorCode
from {{cookiecutter.project_slug}}.core.exceptions import ApplicationError

logger = logging.getLogger(__name__)

_FALLBACK_CODE = ErrorCode.INVALID


def _item(message, code=None) -> dict:
    return {
        "message": str(message),
        "code": str(code) if code else str(_FALLBACK_CODE),
    }


def _item_from_detail(detail) -> dict:
    if isinstance(detail, dict) and "message" in detail:
        return _item(detail.get("message", ""), detail.get("code"))
    return _item(detail, getattr(detail, "code", None))


def _normalize_messages(detail) -> dict:
    """
    Convert DRF/Django error detail into:

    { "<field>": [ {"message": "...", "code": "..."}, ... ] }
    """
    if isinstance(detail, dict):
        messages: dict = {}
        for key, value in detail.items():
            if isinstance(value, (list, tuple)):
                messages[key] = [_item_from_detail(item) for item in value]
            elif isinstance(value, dict) and "message" in value:
                messages[key] = [_item_from_detail(value)]
            elif isinstance(value, dict):
                nested = _normalize_messages(value)
                for nested_key, nested_value in nested.items():
                    flat_key = key if nested_key == "non_field_errors" else f"{key}.{nested_key}"
                    messages[flat_key] = nested_value
            else:
                messages[key] = [_item_from_detail(value)]
        return messages

    if isinstance(detail, (list, tuple)):
        return {"non_field_errors": [_item_from_detail(item) for item in detail]}

    return {"non_field_errors": [_item_from_detail(detail)]}


def _error_response(*, http_status: int, messages: dict) -> Response:
    return Response(
        {
            "success": False,
            "status": http_status,
            "result": [],
            "messages": messages,
        },
        status=http_status,
    )


def api_exception_handler(exc, context):
    """
    Normalize API errors into one envelope:

    {
      "success": false,
      "status": <http_status>,
      "result": [],
      "messages": {
        "<field>": [{"message": "...", "code": "..."}]
      }
    }
    """
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()

    if isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, ApplicationError):
        messages = {
            "non_field_errors": [_item(exc.message, ErrorCode.APPLICATION_ERROR)],
        }
        for key, value in (exc.extra or {}).items():
            if isinstance(value, (list, tuple)):
                messages[key] = [_item_from_detail(item) for item in value]
            else:
                messages[key] = [_item_from_detail(value)]
        return _error_response(http_status=status.HTTP_400_BAD_REQUEST, messages=messages)

    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            "success": False,
            "status": response.status_code,
            "result": [],
            "messages": _normalize_messages(response.data),
        }
        return response

    # Unexpected exception in a DRF view — keep the same envelope, hide internals.
    if context.get("view") is None:
        return None

    logger.exception("Unhandled API exception", exc_info=exc)
    return _error_response(
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        messages={
            "non_field_errors": [
                _item(_("a server error occurred."), ErrorCode.SERVER_ERROR),
            ]
        },
    )
