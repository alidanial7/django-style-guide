"""Generate per-scope models, URLs, permissions, and docs mounts after cookiecutter render."""

from __future__ import annotations

import re
from pathlib import Path

from scopes import scope_pascal, scopes_from_cookiecutter

_HOOKS_DIR = Path(__file__).resolve().parent
_TEMPLATES_DIR = _HOOKS_DIR / "templates"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = content if content.startswith("\n") else f"\n{content}"
    path.write_text(text.lstrip("\n"), encoding="utf-8")
    print(f"  - scoped {path.as_posix()}")


def scaffold_scopes(
    *,
    project_root: Path,
    project_slug: str,
    api_scopes_raw: str,
    use_file_manager: bool,
    use_i18n: bool,
    reverse_proxy: str,
    use_testing: bool = False,
    use_jwt: bool = True,
    user_login_field: str = "email",
) -> list[str]:
    """Materialize multi-scope API surface. Returns normalized scope names."""
    scopes = scopes_from_cookiecutter(api_scopes_raw)
    slug = project_slug

    _write_settings(project_root, scopes, slug)
    _write_api_scope_middleware(project_root)
    _write_scope_registry(project_root, scopes, slug)
    _write_membership_service(project_root, slug)
    _write_permissions(project_root, slug)
    _write_models(project_root, scopes, slug)
    _write_api_urls(project_root, scopes, slug, use_file_manager=use_file_manager)
    for scope in scopes:
        _write_scope_urls(project_root, scope, slug)
        _write_scope_health(project_root, scope, slug)
    _write_config_urls(
        project_root,
        scopes,
        slug,
        use_i18n=use_i18n,
        reverse_proxy=reverse_proxy,
    )
    _write_schema_generators(project_root, scopes, slug)
    _write_scoped_apis_rule(project_root, scopes)
    _register_admin(project_root, scopes, slug)
    _write_add_api_scope_command(project_root, slug)
    if use_testing:
        _write_contract_tests(
            project_root,
            slug,
            use_jwt=use_jwt,
            user_login_field=user_login_field,
        )
    return scopes


def _write_settings(root: Path, scopes: list[str], slug: str) -> None:
    lines = ",\n".join(f'    "{s}"' for s in scopes)
    model_map = ",\n".join(
        f'    "{s}": "users.{scope_pascal(s)}User"' for s in scopes
    )
    _write(
        root / "config" / "settings" / "api_scopes.py",
        f'''
"""API surface scopes (cookiecutter multi-scope mode)."""

API_SCOPES = [
{lines},
]

# Dotted paths to multi-table scope user models (subclass BaseUser).
API_SCOPE_USER_MODELS = {{
{model_map},
}}
''',
    )


def _write_api_scope_middleware(root: Path) -> None:
    _write(
        root / "config" / "api_scope.py",
        '''
"""Resolve ``/api/v1/<scope>/…`` onto ``request.api_scope``."""

from __future__ import annotations

from django.conf import settings


def resolve_api_scope(path: str) -> str | None:
    """Return the configured scope name from an API path, else ``None``."""
    parts = path.strip("/").split("/")
    if len(parts) < 3 or parts[0] != "api" or parts[1] != "v1":
        return None
    candidate = parts[2]
    if candidate in getattr(settings, "API_SCOPES", ()):
        return candidate
    return None


class ApiScopeMiddleware:
    """
    Attach ``request.api_scope`` for multi-scope projects.

    Membership / ``IsScopeMember`` prefer this attribute; path parsing remains
    a fallback for tests that bypass middleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.api_scope = resolve_api_scope(request.path)
        return self.get_response(request)
''',
    )


def _write_scope_registry(root: Path, scopes: list[str], slug: str) -> None:
    mapping = ",\n".join(
        f'    "{s}": "users.{scope_pascal(s)}User"' for s in scopes
    )
    _write(
        root / slug / "users" / "scope_registry.py",
        f'''
"""Map API scope names to their BaseUser subclass."""

from __future__ import annotations

from django.apps import apps
from django.conf import settings

from config.api_scope import resolve_api_scope


SCOPE_USER_MODEL_PATHS = {{
{mapping},
}}


def get_scope_user_model(*, scope: str):
    """Return the concrete scope user model class for ``scope``."""
    try:
        dotted = SCOPE_USER_MODEL_PATHS[scope]
    except KeyError as error:
        raise ValueError(f"Unknown API scope: {{scope!r}}") from error
    return apps.get_model(dotted)


def get_request_scope(request) -> str | None:
    """Prefer ``request.api_scope``; fall back to path parsing."""
    scope = getattr(request, "api_scope", None)
    if scope:
        return scope
    return resolve_api_scope(request.path)
''',
    )


def _write_membership_service(root: Path, slug: str) -> None:
    _write(
        root / slug / "users" / "services" / "scope_membership.py",
        f'''
"""Attach BaseUser rows to per-scope multi-table user models."""

from __future__ import annotations

from django.db import transaction

from {slug}.users.models import BaseUser
from {slug}.users.scope_registry import get_request_scope, get_scope_user_model


@transaction.atomic
def ensure_scope_membership(*, user: BaseUser, scope: str):
    """
    Ensure ``user`` has a row in the scope table.

    Shared identity stays on BaseUser / Profile; scope tables start empty and
    may gain custom fields later. One user may belong to many scopes.
    """
    model = get_scope_user_model(scope=scope)
    existing = model.objects.filter(pk=user.pk).first()
    if existing is not None:
        return existing

    # Multi-table child link is ``<parent_model_name>_ptr`` (e.g. baseuser_ptr).
    parent_link = model._meta.parents[user.__class__]
    scoped = model(**{{parent_link.name: user}})
    scoped.__dict__.update(user.__dict__)
    scoped.save()
    return model.objects.get(pk=user.pk)


def ensure_scope_membership_for_request(*, request, user: BaseUser):
    """No-op when the request is not under ``/api/v1/<scope>/``."""
    scope = get_request_scope(request)
    if not scope:
        return None
    return ensure_scope_membership(user=user, scope=scope)


def user_in_scope(*, user: BaseUser, scope: str) -> bool:
    model = get_scope_user_model(scope=scope)
    return model.objects.filter(pk=user.pk).exists()
''',
    )


def _write_permissions(root: Path, slug: str) -> None:
    _write(
        root / slug / "users" / "permissions.py",
        f'''
"""Scope membership DRF permissions (multi-scope mode)."""

from __future__ import annotations

from rest_framework.permissions import BasePermission


class IsScopeMember(BasePermission):
    """
    Allow authenticated users that belong to the active API scope.

    Uses ``request.api_scope`` (middleware) by default. Pin a scope with
    ``permission_classes = [IsScopeMember.for_scope("admin")]``.
    """

    scope: str | None = None

    @classmethod
    def for_scope(cls, scope: str) -> type[BasePermission]:
        return type(f"IsScopeMember_{{scope}}", (cls,), {{"scope": scope}})

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
        scope = self.scope or getattr(request, "api_scope", None)
        if not scope:
            from {slug}.users.scope_registry import get_request_scope

            scope = get_request_scope(request)
        if not scope:
            return False
        from {slug}.users.services.scope_membership import user_in_scope

        return user_in_scope(user=user, scope=scope)


__all__ = [
    "IsScopeMember",
]
''',
    )


def _write_models(root: Path, scopes: list[str], slug: str) -> None:
    init_imports = [
        "from .base_user import BaseUser",
        "from .profile import Profile",
    ]
    all_names = ['"BaseUser"', '"Profile"']
    for scope in scopes:
        pascal = scope_pascal(scope)
        model_name = f"{pascal}User"
        _write(
            root / slug / "users" / "models" / f"{scope}_user.py",
            f'''
from django.utils.translation import gettext_lazy as _

from {slug}.users.models.base_user import BaseUser


class {model_name}(BaseUser):
    """
    Scope table for ``{scope}``.

    Identity/credentials live on BaseUser; add {scope}-only fields here later.
    """

    class Meta:
        verbose_name = _("{scope} user")
        verbose_name_plural = _("{scope} users")

    def __str__(self) -> str:
        return f"{scope}:{{super().__str__()}}"
''',
        )
        init_imports.append(f"from .{scope}_user import {model_name}")
        all_names.append(f'"{model_name}"')

    social_path = root / slug / "users" / "models" / "social_account.py"
    if social_path.exists():
        init_imports.append("from .social_account import SocialAccount")
        all_names.append('"SocialAccount"')

    all_body = ",\n    ".join(all_names)
    _write(
        root / slug / "users" / "models" / "__init__.py",
        f'''
{chr(10).join(init_imports)}

__all__ = [
    {all_body},
]
''',
    )


def _write_api_urls(
    root: Path,
    scopes: list[str],
    slug: str,
    *,
    use_file_manager: bool,
) -> None:
    scope_paths = "\n".join(
        f'    path("{s}/", include(("{slug}.api.{s}_urls", "{s}"))),' for s in scopes
    )
    files_path = ""
    if use_file_manager:
        files_path = f'''
    path(
        "files/",
        include(("{slug}.file_manager.urls.file_manager_url", "file_manager")),
    ),'''
    _write(
        root / slug / "api" / "urls.py",
        f'''
from django.urls import include, path

urlpatterns = [
    # Platform (unscoped)
    path("", include(("{slug}.core.urls", "core"))),{files_path}
    # Per-scope domain surfaces: /api/v1/<scope>/auth|users|…
{scope_paths}
]
''',
    )


def _write_scope_urls(root: Path, scope: str, slug: str) -> None:
    _write(
        root / slug / "api" / f"{scope}_urls.py",
        f'''
"""Routes under ``/api/v1/{scope}/``."""

from django.urls import include, path

urlpatterns = [
    path("", include(("{slug}.core.urls.{scope}_core_url", "{scope}_core"))),
    path("auth/", include(("{slug}.users.urls.auth_url", "auth"))),
    path("users/", include(("{slug}.users.urls.users_url", "users"))),
]
''',
    )


def _write_scope_health(root: Path, scope: str, slug: str) -> None:
    pascal = scope_pascal(scope)
    _write(
        root / slug / "core" / "urls" / f"{scope}_core_url.py",
        f'''
from django.urls import path

from {slug}.core.apis.{scope}.health.{scope}_health_apis import {pascal}HealthApiView

app_name = "{scope}_core"

urlpatterns = [
    path("health/", {pascal}HealthApiView.as_view(), name="health"),
]
''',
    )
    _write(root / slug / "core" / "apis" / scope / "__init__.py", "")
    _write(
        root / slug / "core" / "apis" / scope / "health" / "__init__.py",
        f'from .{scope}_health_apis import {pascal}HealthApiView\n\n__all__ = ["{pascal}HealthApiView"]\n',
    )
    _write(
        root / slug / "core" / "apis" / scope / "health" / f"{scope}_health_apis.py",
        f'''
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import AllowAny

from {slug}.common.http.schema import envelope_serializer
from {slug}.core.apis.health.health_apis import HealthApi


@extend_schema_view(
    get=extend_schema(
        tags=["{scope}"],
        summary="{pascal} scoped health (sample)",
        description=(
            "Sample probe under ``/api/v1/{scope}/health/``. "
            "Prefer ``/api/v1/health/`` for real platform probes."
        ),
        responses=envelope_serializer("{pascal}HealthEnvelope", HealthApi.OutputSerializer),
    )
)
class {pascal}HealthApiView(HealthApi):
    """Scoped-API sample health for the ``{scope}`` surface."""

    permission_classes = [AllowAny]
''',
    )


def _write_config_urls(
    root: Path,
    scopes: list[str],
    slug: str,
    *,
    use_i18n: bool,
    reverse_proxy: str,
) -> None:
    gen_imports = ", ".join(f"{scope_pascal(s)}SchemaGenerator" for s in scopes)
    scope_docs = []
    for scope in scopes:
        pascal = scope_pascal(scope)
        scope_docs.append(
            f'''        path(
            "{scope}/schema/",
            SpectacularAPIView.as_view(
                api_version="v1",
                generator_class={pascal}SchemaGenerator,
            ),
            name="schema-{scope}",
        ),
        path(
            "{scope}/",
            SpectacularSwaggerView.as_view(url_name="schema-{scope}"),
            name="swagger-ui-{scope}",
        ),'''
        )
    i18n_line = (
        '    path("i18n/", include("django.conf.urls.i18n")),\n' if use_i18n else ""
    )
    else_media = ""
    if reverse_proxy == "none":
        else_media = '''
else:
    # No reverse proxy: Django serves uploaded media from the volume.
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]
'''
    _write(
        root / "config" / "urls.py",
        f'''
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from {slug}.common.http.schema import {gen_imports}

urlpatterns = [
    path("admin/", admin.site.urls),
{i18n_line}    path("api/v1/", include(("{slug}.api.urls", "api"))),
]

if settings.DEBUG:
    # OpenAPI under /api/docs/ (+ /api/docs/<scope>/).
    docs_urlpatterns = [
        path("schema/", SpectacularAPIView.as_view(api_version="v1"), name="schema"),
        path("", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
{chr(10).join(scope_docs)}
    ]
    urlpatterns = [
        path("api/docs/", include(docs_urlpatterns)),
        *urlpatterns,
    ]
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve,
            {{"document_root": settings.MEDIA_ROOT}},
        ),
    ]
{else_media}''',
    )


def _write_schema_generators(root: Path, scopes: list[str], slug: str) -> None:
    path = root / slug / "common" / "http" / "schema.py"
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r"\nSiteSchemaGenerator = make_scoped_schema_generator\([^\)]*\)\n?",
        "\n",
        text,
    )
    text = re.sub(
        r"\n\w+SchemaGenerator = make_scoped_schema_generator\([^\n]*\)\n?",
        "\n",
        text,
    )
    gens = "\n".join(
        f'{scope_pascal(s)}SchemaGenerator = make_scoped_schema_generator("/api/v1/{s}")'
        for s in scopes
    )
    text = text.rstrip() + "\n\n" + gens + "\n"
    path.write_text(text, encoding="utf-8")
    print(f"  - scoped {path.as_posix()} generators")


def _register_admin(root: Path, scopes: list[str], slug: str) -> None:
    admin_path = root / slug / "users" / "admin.py"
    if not admin_path.exists():
        return
    text = admin_path.read_text(encoding="utf-8")
    extras = []
    for scope in scopes:
        pascal = scope_pascal(scope)
        model = f"{pascal}User"
        if f"class {pascal}UserAdmin" not in text:
            extras.append(
                f"""

@admin.register({model})
class {pascal}UserAdmin(admin.ModelAdmin):
    search_fields = ("email",)
"""
            )
    if not extras:
        return

    added = ", ".join(f"{scope_pascal(s)}User" for s in scopes)

    def _expand(match: re.Match[str]) -> str:
        names = match.group(1)
        if scope_pascal(scopes[0]) + "User" in names:
            return match.group(0)
        return f"from {slug}.users.models import {names}, {added}"

    text, count = re.subn(
        rf"from {re.escape(slug)}\.users\.models import ([^\n]+)",
        _expand,
        text,
        count=1,
    )
    if count == 0:
        return
    text = text.rstrip() + "".join(extras) + "\n"
    admin_path.write_text(text, encoding="utf-8")
    print(f"  - scoped {admin_path.as_posix()} registrations")


def _write_scoped_apis_rule(root: Path, scopes: list[str]) -> None:
    listed = ", ".join(f"`{s}`" for s in scopes)
    _write(
        root / ".cursor" / "rules" / "scoped-apis.mdc",
        f'''
---
description: Multi-scope API surfaces, scope users, docs mounts
globs: "**/api/**/*.py,**/apis/**/*.py,**/users/models/*_user.py,**/users/scope_registry.py,**/users/services/scope_membership.py,**/users/permissions.py,**/config/settings/api_scopes.py,**/config/api_scope.py,**/config/urls.py,**/commands/management/commands/add_api_scope.py"
alwaysApply: false
---

# Scoped APIs

Enabled scopes: {listed}.

- Domain routes live under `/api/v1/<scope>/…` (auth, users, future apps). Do **not** mount domain APIs at bare `/api/v1/` when multi-scope is on.
- Platform health stays at `/api/v1/health/`. Each scope also has a sample `/api/v1/<scope>/health/`.
- Docs: `/api/docs/` (full) · `/api/docs/<scope>/` (filtered).
- Identity: shared `BaseUser` + `Profile`. Scope tables (`*User` MTI subclasses) start empty — add scope-only fields there. One user may belong to many scopes.
- `ApiScopeMiddleware` sets `request.api_scope`. Auth/register calls `ensure_scope_membership_for_request`.
- Gate scoped views with `IsScopeMember` (or `IsScopeMember.for_scope("…")`).
- Add a scope later: `python manage.py add_api_scope <name>` then `makemigrations` / `migrate`.
- Changing scope conventions → update **this rule file** + `apis` / `auth` / `commands` rules in the **same** change.

Deep: `docs/style-guide/domain/apis.md` · `docs/style-guide/domain/urls.md` · `docs/style-guide/http/swagger.md` · `docs/style-guide/ops/commands.md`
''',
    )



def _write_add_api_scope_command(root: Path, slug: str) -> None:
    src = _TEMPLATES_DIR / "add_api_scope.py"
    dest = (
        root
        / slug
        / "commands"
        / "management"
        / "commands"
        / "add_api_scope.py"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"  - scoped {dest.as_posix()}")


def _write_contract_tests(
    root: Path,
    slug: str,
    *,
    use_jwt: bool,
    user_login_field: str,
) -> None:
    text = (_TEMPLATES_DIR / "test_scope_contracts.py").read_text(encoding="utf-8")
    text = text.replace("__PROJECT_SLUG__", slug)

    if user_login_field == "username":
        helpers = '''
def _login_payload(user, *, password: str = "Password1!x") -> dict:
    return {"username": user.username, "password": password}


def _register_payload(*, email: str, suffix: str) -> dict:
    return {
        "username": f"u_{suffix}",
        "email": email,
        "password": "Password1!x",
        "confirm_password": "Password1!x",
        "bio": "hello",
    }
'''
    else:
        helpers = '''
def _login_payload(user, *, password: str = "Password1!x") -> dict:
    return {"email": user.email, "password": password}


def _register_payload(*, email: str, suffix: str) -> dict:
    return {
        "email": email,
        "password": "Password1!x",
        "confirm_password": "Password1!x",
        "bio": "hello",
    }
'''
    text = text.replace("# __LOGIN_HELPERS__", helpers.strip())

    if use_jwt:
        jwt_test = '''
    def test_login_ensures_membership_for_active_scope(self, api_client):
        scopes = list(settings.API_SCOPES)
        assert len(scopes) >= 2
        primary, other = scopes[0], scopes[1]
        user = BaseUserFactory()
        assert user_in_scope(user=user, scope=primary) is False

        login = api_client.post(
            api_reverse("auth:login", scope=primary),
            data=_login_payload(user),
            format="json",
        )
        assert login.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user_in_scope(user=user, scope=primary) is True
        assert user_in_scope(user=user, scope=other) is False

        login_other = api_client.post(
            api_reverse("auth:login", scope=other),
            data=_login_payload(user),
            format="json",
        )
        assert login_other.status_code == status.HTTP_200_OK
        assert user_in_scope(user=user, scope=other) is True
'''
    else:
        jwt_test = ""
    text = text.replace("    # __JWT_LOGIN_TEST__", jwt_test.rstrip())

    dest = root / slug / "users" / "tests" / "test_scope_contracts.py"
    _write(dest, text)
