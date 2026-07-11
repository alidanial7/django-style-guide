# Permissions

## Default stack

DRF defaults are set in `config/settings/drf.py` (authentication class only — **not** a global `IsAuthenticated` permission). Each view chooses its own permission level.

{%- if cookiecutter.use_jwt == "y" %}
Default authentication: `JWTAuthentication`.
{%- else %}
Default authentication: `SessionAuthentication`.
{%- endif %}

## `ApiAuthMixin`

Authenticated endpoints inherit `ApiAuthMixin` from `{{cookiecutter.project_slug}}.api.mixins`:

```python
class ApiAuthMixin:
    authentication_classes = [...]  # JWT or Session, matching project generation
    permission_classes = (IsAuthenticated,)
```

Usage:

```python
from {{cookiecutter.project_slug}}.api.mixins import ApiAuthMixin

class UsersProfileApi(ApiAuthMixin, APIView):
    ...
```

Public endpoints (login, register, password reset) **do not** use the mixin. They rely on empty / default permission classes (`AllowAny` effectively for unauthenticated access).

## Custom permissions

Add DRF permission classes when you need object-level or role checks:

1. Prefer a dedicated module under the domain app (e.g. `users/permissions.py`) or next to the API feature.
2. Compose them on the view: `permission_classes = (IsAuthenticated, IsOwner)`.
3. Keep permission logic out of serializers and out of selectors.

Example sketch:

```python
from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner_id == request.user.id
```

Raise Django/`rest_framework` permission denied as usual — `api_exception_handler` normalizes them into the envelope.

## Admin vs API

Django admin uses staff/superuser flags independently of API mixins. Do not assume `is_staff` grants API access unless you add an explicit permission class.

## CSRF (session auth)

{%- if cookiecutter.use_jwt == "y" %}
JWT Bearer clients are not affected by CSRF. If you later add cookie-based session endpoints, remember CSRF for unsafe methods.
{%- else %}
Browser clients using session cookies must send a valid CSRF token on unsafe methods (`POST` / `PATCH` / `PUT` / `DELETE`).
{%- endif %}
