from __future__ import annotations

from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error
from rest_framework.views import exception_handler

from {{cookiecutter.project_slug}}.core.exceptions import ApplicationError


def _normalize_messages(detail) -> dict:
    if isinstance(detail, dict):
        messages: dict = {}
        for key, value in detail.items():
            if isinstance(value, (list, tuple)):
                messages[key] = [str(item) for item in value]
            elif isinstance(value, dict):
                nested = _normalize_messages(value)
                for nested_key, nested_value in nested.items():
                    messages[f"{key}.{nested_key}" if nested_key != "non_field_errors" else key] = nested_value
            else:
                messages[key] = [str(value)]
        return messages

    if isinstance(detail, (list, tuple)):
        return {"non_field_errors": [str(item) for item in detail]}

    return {"non_field_errors": [str(detail)]}


def api_exception_handler(exc, context):
    """
    Normalize API errors into:

    {
      "success": false,
      "status": <http_status>,
      "result": [],
      "messages": { "<field>": ["..."], "non_field_errors": ["..."] }
    }
    """
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()

    if isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, ApplicationError):
        return Response(
            {
                "success": False,
                "status": status.HTTP_400_BAD_REQUEST,
                "result": [],
                "messages": {"non_field_errors": [str(exc.message)], **{k: [str(v)] for k, v in (exc.extra or {}).items()}},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    response = exception_handler(exc, context)
    if response is None:
        return response

    response.data = {
        "success": False,
        "status": response.status_code,
        "result": [],
        "messages": _normalize_messages(response.data),
    }
    return response
