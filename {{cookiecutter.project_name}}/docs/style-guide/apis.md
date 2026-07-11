# APIs & serializers

APIs are thin: authenticate/authorize, validate input, call selector/service, return `api_response`.

## View pattern

```python
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView

from {{cookiecutter.project_slug}}.api.mixins import ApiAuthMixin
from {{cookiecutter.project_slug}}.common.http import api_response


class UsersProfileApi(ApiAuthMixin, APIView):
    @extend_schema(tags=USERS_TAGS, summary="Current user", responses=UsersProfileOutputSerializer)
    def get(self, request):
        profile = get_profile(user=request.user)
        return api_response(
            data=UsersProfileOutputSerializer(profile, context={"request": request}).data
        )

    @extend_schema(
        tags=USERS_TAGS,
        summary="Update current user profile",
        request=UsersProfileUpdateInputSerializer,
        responses=UsersProfileOutputSerializer,
    )
    def patch(self, request):
        serializer = UsersProfileUpdateInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        profile = profile_update(profile=get_profile(user=request.user), **serializer.validated_data)
        return api_response(
            data=UsersProfileOutputSerializer(profile, context={"request": request}).data
        )
```

### Rules

- Prefer `APIView` (or small viewsets if the team agrees) over fat generic CBVs that hide business logic.
- Always `serializer.is_valid(raise_exception=True)`.
- Always return via `api_response` (or pagination helpers that wrap it).
- Use `ApiAuthMixin` for authenticated endpoints (see [Permissions](permissions.md)).
- Public endpoints omit the mixin and set throttling when abuse is likely (see [Throttling](throttling.md)).

## Serializers: input vs output

Split serializers by direction:

| Type | Role |
|------|------|
| `*InputSerializer` | Request body / query validation |
| `*OutputSerializer` | Response payload shaping |

Do not use one ModelSerializer for both unless the shapes are identical and simple.

### Input serializer rules

- Field validators: reuse domain `PASSWORD_VALIDATORS` / `*Validator` lists.
- Cross-field rules: `validate()` with **field-keyed** errors and `gettext_lazy` messages.
- Platform vs domain codes:

```python
# missing input → ErrorCode.REQUIRED (platform)
# password mismatch → UserErrorCode.PASSWORD_MISMATCH (domain)
raise serializers.ValidationError(
    {"confirm_password": [_("confirm password is not equal to password")]},
    code=UserErrorCode.PASSWORD_MISMATCH,
)
```

- Do **not** check uniqueness in serializers — rely on DB + integrity mapping.
- Do **not** encode permission checks in serializers.

### Output serializer rules

- Use `SerializerMethodField` + selectors for derived values (e.g. avatar URL).
- Annotate method fields with `@extend_schema_field` for OpenAPI accuracy.
- Pass `context={"request": request}` when absolute URLs are needed.

## File layout

```text
apis/
└── users/
    └── profile/
        ├── users_profile_apis.py
        ├── users_profile_serializers.py
        └── tests/
```

Name files with the app + feature prefix for greppability.

## Swagger tags

Define tags once in `<app>/constants.py` and pass them to `@extend_schema(tags=...)`:

```python
USERS_TAGS = ["users"]
AUTH_TAGS = ["auth"]
```

See [Swagger / OpenAPI](swagger.md).

## Parsers

When accepting uploads (avatar), include multipart parsers explicitly:

```python
parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
```

## Nested OutputSerializer on the view (health)

For tiny system endpoints, an inner `OutputSerializer` on the view class is fine (see `HealthApi`). Prefer separate modules for domain features.
