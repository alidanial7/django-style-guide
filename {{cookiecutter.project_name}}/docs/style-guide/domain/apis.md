# APIs & serializers

Thin HTTP layer: serializers, OpenAPI, parsers, throttling. Business rules and ORM writes live in [selectors](selectors.md) / [services](services.md). Always return the [API envelope](../http/api-envelope.md).

---

## Rules

### Folder layout mirrors URL

Under `<app>/apis/`, folders follow real URL path segments. Do not invent a parallel “feature nickname” tree.

```text
URL:  /api/v1/pos/wallet/charge/init/
Dirs: apis/pos/wallet/charge/init/
```

| Rule | Detail |
|------|--------|
| One segment → one folder | Nest actions deeper (`…/charge/init/`, `…/id/revoke/`) |
| Path param | Folder `id/` for `/…/<id>/…` |
| Kebab URL | Snake folder: `/pos-menu/` → `apis/pos_menu/` |
| Leaf files | `*_apis.py` + `*_serializers.py` + `tests/` in **that** folder |
| File prefix | Snake path of the leaf: `pos_wallet_balance_apis.py` |
| Tests | Next to the leaf only — never root `apis/tests/` |
| List filters | `<Entity>Filter` in `*_search_filters.py`; apply in the view after `list_*()` |

```text
apis/
├── pos/
│   ├── pos_apis.py / pos_serializers.py / tests/
│   ├── heartbeat/   # leaf files + tests/
│   └── id/
│       ├── pos_id_apis.py / pos_id_serializers.py / tests/
│       └── revoke/  # leaf files + tests/
└── users/
    ├── register/    # leaf files + tests/
    └── profile/     # leaf files + tests/
```

### Client / surface-scoped APIs (`/api/v1/<scope>/…`)

For scoped surfaces (`/api/v1/site/…`, `/api/v1/admin/…`):

1. **Directory mirror** — `apis/<scope>/…` matches URL segments (`/api/v1/site/…/cities/` → `…/apis/site/cities/`)
2. **Files** — scope prefix: `site_cities_apis.py`, `site_cities_serializers.py`, `tests/test_site_cities_apis.py`
3. **Classes** — `SiteCityListApiView`, `SiteCityOutputSerializer`, `SiteCityListEnvelope`
4. **OpenAPI** — `@extend_schema_serializer(component_name="Site…")` to avoid codegen collisions
5. **URLs** — `urls/site_<app>_url.py` mounted in `{{cookiecutter.project_slug}}/api/site_urls.py`
6. **Leaf tests** — every leaf (collection **and** `id/`) has its own `tests/`; never aggregate detail into collection tests

### `APIView` class naming

Plain `APIView` with explicit verbs. Names mirror DRF generics; inheritance of generics is **not** required.

| Class | Methods | URL |
|-------|---------|-----|
| `{Entity}ListCreateApiView` | `GET` list + `POST` create | `/posts/` |
| `{Entity}RetrieveUpdateDestroyApiView` | `GET`/`PUT`/`PATCH`/`DELETE` | `/posts/<id>/` |

`{Entity}` = PascalCase **singular** (`Post`). Prefer ListCreate + RUD; split only when needed (`ListApiView`, `CreateApiView`, `RetrieveApiView`, `UpdateApiView`, `DestroyApiView`, `RetrieveUpdateApiView`). Actions (login, register, health, “me”) → descriptive `*ApiView` (`UserRegisterApiView`, `ProfileRetrieveUpdateApiView`).

Do **not** use `PostsListCreateApiView`, `PostCRUDView`, bare `PostList`, or one mega-class for `/` and `/<id>/`.

### View contract

| ✅ Do | ❌ Don’t |
|-------|---------|
| `serializer.is_valid(raise_exception=True)` | Manual error dicts |
| `return api_response(...)` | `return Response(serializer.data)` |
| `envelope_serializer(...)` in `@extend_schema(responses=...)` | Document only the inner serializer as the body |
| Services/selectors + `data=validated_data` (TypedDict) | ORM in view / `serializer.save()` / dataclass DTOs |
| `@extend_schema` on each handler | Undocumented endpoints |
| `ApiAuthMixin` when auth required | Ad-hoc auth in handlers |
| `AllowAny` on public routes | Assuming new views are public |
| FilterSet in view after `list_*()` | Filters inside selector / raw query params only |

Always split **Input** vs **Output** serializers. Drop HTTP-only fields (`confirm_password`) before `validated_data`. Uniqueness, permissions, and writes do **not** belong in serializers. For uploads: `parser_classes = [MultiPartParser, FormParser, JSONParser]`.

---

## Example

{%- if cookiecutter.use_uuid_pk == "y" %}
```python
# blogs/apis/posts/posts_apis.py → /posts/
# blogs/apis/posts/id/posts_id_apis.py → /posts/<id>/
from uuid import UUID

from rest_framework.views import APIView

from {{cookiecutter.project_slug}}.api.mixins import ApiAuthMixin
from {{cookiecutter.project_slug}}.common.http import api_response
from {{cookiecutter.project_slug}}.common.http.schema import envelope_serializer


class PostListCreateApiView(ApiAuthMixin, APIView):
    def get(self, request): ...
    def post(self, request): ...


class PostRetrieveUpdateDestroyApiView(ApiAuthMixin, APIView):
    def get(self, request, post_id: UUID): ...
    def put(self, request, post_id: UUID): ...
    def patch(self, request, post_id: UUID): ...
    def delete(self, request, post_id: UUID): ...
```

```python
# blogs/urls/blogs_url.py
path("posts/", PostListCreateApiView.as_view(), name="posts-list-create"),
path("posts/<uuid:post_id>/", PostRetrieveUpdateDestroyApiView.as_view(), name="posts-detail"),
```
{%- else %}
```python
# blogs/apis/posts/posts_apis.py → /posts/
# blogs/apis/posts/id/posts_id_apis.py → /posts/<id>/
from rest_framework.views import APIView

from {{cookiecutter.project_slug}}.api.mixins import ApiAuthMixin
from {{cookiecutter.project_slug}}.common.http import api_response
from {{cookiecutter.project_slug}}.common.http.schema import envelope_serializer


class PostListCreateApiView(ApiAuthMixin, APIView):
    def get(self, request): ...
    def post(self, request): ...


class PostRetrieveUpdateDestroyApiView(ApiAuthMixin, APIView):
    def get(self, request, post_id: int): ...
    def put(self, request, post_id: int): ...
    def patch(self, request, post_id: int): ...
    def delete(self, request, post_id: int): ...
```

```python
# blogs/urls/blogs_url.py
path("posts/", PostListCreateApiView.as_view(), name="posts-list-create"),
path("posts/<int:post_id>/", PostRetrieveUpdateDestroyApiView.as_view(), name="posts-detail"),
```
{%- endif %}

```python
# users/apis/users/profile/users_profile_apis.py
class UsersProfileApi(ApiAuthMixin, APIView):
    @extend_schema(
        tags=USERS_TAGS,
        summary="Current user",
        responses=envelope_serializer("UsersProfileEnvelope", UsersProfileOutputSerializer),
    )
    def get(self, request):
        profile = get_profile(user=request.user)
        return api_response(
            data=UsersProfileOutputSerializer(profile, context={"request": request}).data
        )

    @extend_schema(
        tags=USERS_TAGS,
        request=UsersProfileUpdateInputSerializer,
        responses=envelope_serializer("UsersProfileUpdateEnvelope", UsersProfileOutputSerializer),
    )
    def patch(self, request):
        serializer = UsersProfileUpdateInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        profile = profile_update(
            profile=get_profile(user=request.user),
            data=serializer.validated_data,
        )
        return api_response(
            data=UsersProfileOutputSerializer(profile, context={"request": request}).data
        )
```

---

## Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| Fat view / ORM in view | Service + selector |
| One serializer for input+output with secrets | Split Input/Output |
| `return Response(data)` | `api_response` |
| Uniqueness in serializer / perms in `validate()` | DB + integrity / permission classes |
| Missing `@extend_schema` or bare inner `responses` | `@extend_schema` + `envelope_serializer` |
| `views.py` / flat folders vs nested URLs | `apis/` mirrors URL segments |
| Raw query-param filtering | `*_search_filters.py` + FilterSet in view |
| Dataclass DTO / field-by-field `.get` | TypedDict + `"field" in data` — [Types](types.md) |
| Scoped route at `apis/` root / shared collection+id tests | Mirror `<scope>/…` + leaf `tests/` per leaf |

### Checklist: new endpoint

1. `apis/` folders mirror the URL (including `<scope>/` when scoped)
2. Input + Output serializers + leaf `tests/`
3. Named `APIView` + `@extend_schema` + tags from `constants.py`
4. `ApiAuthMixin` / throttle; `AllowAny` only when public
5. Selector/service only — `data=validated_data` (TypedDict)
6. `api_response` with correct status
7. Register in `<app>/urls/` (+ scoped `api/<scope>_urls.py` if needed)
8. API tests under the leaf

---

## Related

| Doc | Why |
|-----|-----|
| [API envelope](../http/api-envelope.md) | JSON contract |
| [Types](types.md) | Serializer → TypedDict → service |
| [Validation](validation.md) · [Errors](errors.md) | Validators, codes, integrity |
| [Permissions](../http/permissions.md) | `ApiAuthMixin` |
| [Swagger](../http/swagger.md) · [Pagination](../http/pagination.md) · [Filtering](../http/filtering.md) · [Throttling](../http/throttling.md) | HTTP extras |
| [URLs](urls.md) · [Testing](../ops/testing.md) | Paths / API tests |
