from __future__ import annotations

from typing import Any

from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.utils import inline_serializer
from rest_framework import serializers

_ENVELOPE_SERIALIZER_CACHE: dict[tuple[str, Any, bool], Any] = {}
_PAGINATED_PAGE_CACHE: dict[tuple[str, Any], Any] = {}


def envelope_serializer(
    name: str,
    result: type[serializers.BaseSerializer] | serializers.Field,
    *,
    many: bool = False,
):
    """Document the runtime success envelope around a result payload."""
    cache_key = (name, getattr(result, "__name__", str(result)), many)
    if cache_key in _ENVELOPE_SERIALIZER_CACHE:
        return _ENVELOPE_SERIALIZER_CACHE[cache_key]

    result_field: Any
    if isinstance(result, serializers.Field):
        result_field = result
    elif many:
        result_field = result(many=True)
    else:
        result_field = result()

    serializer_instance = inline_serializer(
        name=name,
        fields={
            "success": serializers.BooleanField(),
            "status": serializers.IntegerField(),
            "result": result_field,
            "messages": serializers.DictField(child=serializers.JSONField(), required=False),
        },
    )
    _ENVELOPE_SERIALIZER_CACHE[cache_key] = serializer_instance
    return serializer_instance


def paginated_envelope_serializer(name: str, item: type[serializers.BaseSerializer]):
    """OpenAPI helper for limit/offset list ``result`` pages inside the envelope."""
    cache_key = (name, getattr(item, "__name__", str(item)))
    if cache_key not in _PAGINATED_PAGE_CACHE:
        _PAGINATED_PAGE_CACHE[cache_key] = inline_serializer(
            name=f"{name}Page",
            fields={
                "limit": serializers.IntegerField(),
                "offset": serializers.IntegerField(),
                "count": serializers.IntegerField(),
                "next": serializers.URLField(allow_null=True),
                "previous": serializers.URLField(allow_null=True),
                "results": item(many=True),
            },
        )
    return envelope_serializer(name, _PAGINATED_PAGE_CACHE[cache_key])


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


class PrefixFilteredSchemaGenerator(SchemaGenerator):
    """Filter OpenAPI paths by URL prefix (per-client / portal schemas)."""

    allowed_prefixes: tuple[str, ...] = ()

    def _get_paths_and_endpoints(self):
        endpoints = super()._get_paths_and_endpoints()
        if not self.allowed_prefixes:
            return endpoints
        return [
            (path, path_regex, method, view)
            for path, path_regex, method, view in endpoints
            if any(path == prefix or path.startswith(f"{prefix}/") for prefix in self.allowed_prefixes)
        ]


def make_scoped_schema_generator(*prefixes: str) -> type[PrefixFilteredSchemaGenerator]:
    """
    Build a schema generator limited to ``/api/v1/<scope>/…`` paths.

    Mount the matching Swagger UI at ``/api/docs/<scope>/`` (DEBUG only), e.g.
    ``/api/docs/admin/``, ``/api/docs/factory/``.
    """

    class _ScopedSchemaGenerator(PrefixFilteredSchemaGenerator):
        allowed_prefixes = tuple(prefixes)

    _ScopedSchemaGenerator.__name__ = "ScopedSchemaGenerator"
    _ScopedSchemaGenerator.__qualname__ = "ScopedSchemaGenerator"
    return _ScopedSchemaGenerator
