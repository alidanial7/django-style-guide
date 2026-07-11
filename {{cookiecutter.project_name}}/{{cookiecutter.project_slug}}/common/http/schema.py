from __future__ import annotations

from typing import Any

from drf_spectacular.utils import inline_serializer
from rest_framework import serializers


def envelope_serializer(name: str, result: type[serializers.BaseSerializer] | serializers.Field, *, many: bool = False):
    """
    OpenAPI helper: document the runtime success envelope around a result payload.

    Runtime responses always look like::

        {"success": true, "status": 200, "result": <payload>, "messages": {}}

    Spectacular alone only sees the inner serializer — wrap it with this helper in
    ``@extend_schema(responses=...)`` so clients and agents see the real contract.
    """
    result_field: Any
    if isinstance(result, serializers.Field):
        result_field = result
    elif many:
        result_field = result(many=True)
    else:
        result_field = result()

    return inline_serializer(
        name=name,
        fields={
            "success": serializers.BooleanField(),
            "status": serializers.IntegerField(),
            "result": result_field,
            "messages": serializers.DictField(child=serializers.JSONField(), required=False),
        },
    )


def envelope_error_serializer(name: str = "ApiErrorEnvelope"):
    """OpenAPI helper for the shared error envelope shape."""
    message_item = inline_serializer(
        name=f"{name}MessageItem",
        fields={
            "message": serializers.CharField(),
            "code": serializers.CharField(),
        },
    )
    return inline_serializer(
        name=name,
        fields={
            "success": serializers.BooleanField(),
            "status": serializers.IntegerField(),
            "result": serializers.ListField(child=serializers.JSONField(), required=False),
            "messages": serializers.DictField(child=serializers.ListField(child=message_item)),
        },
    )
