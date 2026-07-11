# Swagger / OpenAPI

This project uses [drf-spectacular](https://drf-spectacular.readthedocs.io/) for schema generation.

## Where it is available

Swagger UI, ReDoc, and the raw schema are mounted in `config/urls.py` **only when `DEBUG=True`**:

| URL | Description |
|-----|-------------|
| http://localhost:8000/ | Swagger UI |
| http://localhost:8000/redoc/ | ReDoc |
| http://localhost:8000/schema/ | OpenAPI schema |

They are **not** exposed in production settings.

## Settings

`config/settings/swagger.py` → `SPECTACULAR_SETTINGS`:

- `TITLE`, `VERSION`
- `SERVE_INCLUDE_SCHEMA`: `False`
- Swagger UI: `deepLinking`, `persistAuthorization`
{%- if cookiecutter.use_jwt == "y" %}
- `APPEND_COMPONENTS.securitySchemes.BearerAuth` (HTTP bearer JWT) for Authorize in Swagger UI
{%- endif %}

DRF uses `"DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema"` (`config/settings/drf.py`).

## Annotating endpoints

Use `@extend_schema` on each HTTP method:

```python
@extend_schema(
    tags=USERS_TAGS,
    summary="Register a new user",
    request=UsersRegisterInputSerializer,
    responses=UsersRegisterOutputSerializer,
)
def post(self, request):
    ...
```

For `SerializerMethodField`, add `@extend_schema_field(...)` so the schema type is correct.

## Tags

Define tags in the app `constants.py` and reuse them — keeps the Swagger sidebar stable.

System endpoints (health) use tags like `["system"]` inline or via core constants.

## Envelope vs schema

Spectacular documents serializer shapes. The runtime success/error **envelope** (`success` / `status` / `result` / `messages`) wraps those payloads. When documenting errors for clients, point them at [API response envelope](api-envelope.md); optionally add spectacular response examples later if the team wants them in the schema.
