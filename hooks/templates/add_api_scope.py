"""Add a new API scope to an existing multi-scope project."""

from __future__ import annotations

import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

_COMMANDS_APP_DIR = Path(__file__).resolve().parents[2]
_PROJECT_PACKAGE_DIR = _COMMANDS_APP_DIR.parent
_PROJECT_ROOT = _PROJECT_PACKAGE_DIR.parent
_PROJECT_SLUG = _PROJECT_PACKAGE_DIR.name

_SCOPE_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_RESERVED = frozenset(
    {
        "api",
        "v1",
        "docs",
        "schema",
        "static",
        "media",
        "health",
        "i18n",
        "auth",
        "users",
        "files",
    }
)


def _pascal(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_") if part)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.lstrip("\n"), encoding="utf-8")


class Command(BaseCommand):
    help = (
        "Scaffold a new API scope (MTI user model, URLs, health, docs, migration). "
        "Then run migrate."
    )

    def add_arguments(self, parser):
        parser.add_argument("scope", type=str, help="Lowercase scope name (e.g. customer)")
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite generated files if they already exist",
        )

    def handle(self, *args, **options):
        if not getattr(settings, "API_SCOPES", None):
            raise CommandError(
                "This project was not generated with use_scoped_apis=y "
                "(API_SCOPES missing)."
            )
        scope = (options["scope"] or "").strip().lower()
        force = options["force"]
        self._validate(scope)
        if scope in settings.API_SCOPES and not force:
            raise CommandError(
                f"Scope {scope!r} already listed in API_SCOPES. "
                "Pass --force to rewrite scaffold files."
            )

        pascal = _pascal(scope)
        model_name = f"{pascal}User"
        self.stdout.write(f"Adding API scope {scope!r}…")

        self._write_model(scope, pascal, model_name, force=force)
        self._patch_models_init(scope, model_name)
        self._write_scope_urls(scope, force=force)
        self._write_scope_health(scope, pascal, force=force)
        self._patch_api_urls(scope)
        self._patch_settings(scope, model_name)
        self._patch_scope_registry(scope, model_name)
        self._patch_schema(scope, pascal)
        self._patch_config_urls(scope, pascal)
        self._patch_admin(scope, pascal, model_name)
        self._patch_scoped_rule(scope)
        self._write_migration(scope, model_name)

        self.stdout.write(self.style.SUCCESS(f"Scope {scope!r} scaffolded."))
        self.stdout.write("Next: python manage.py migrate")

    def _validate(self, scope: str) -> None:
        if not _SCOPE_NAME_RE.match(scope):
            raise CommandError(
                f"Invalid scope {scope!r}. Use lowercase letters/digits/underscore."
            )
        if scope in _RESERVED:
            raise CommandError(f"Scope {scope!r} is reserved for platform routes.")

    def _write_model(self, scope: str, pascal: str, model_name: str, *, force: bool) -> None:
        path = _PROJECT_PACKAGE_DIR / "users" / "models" / f"{scope}_user.py"
        if path.exists() and not force:
            self.stdout.write(f"  skip existing {path.relative_to(_PROJECT_ROOT)}")
            return
        _write(
            path,
            f'''
from django.utils.translation import gettext_lazy as _

from {_PROJECT_SLUG}.users.models.base_user import BaseUser


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
        self.stdout.write(f"  wrote {path.relative_to(_PROJECT_ROOT)}")

    def _patch_models_init(self, scope: str, model_name: str) -> None:
        path = _PROJECT_PACKAGE_DIR / "users" / "models" / "__init__.py"
        text = path.read_text(encoding="utf-8")
        import_line = f"from .{scope}_user import {model_name}"
        if import_line not in text:
            text = text.replace(
                "from .profile import Profile\n",
                f"from .profile import Profile\n{import_line}\n",
                1,
            )
        token = f'"{model_name}"'
        if token not in text:
            text = text.replace(
                '"Profile",',
                f'"Profile",\n    {token},',
                1,
            )
        path.write_text(text, encoding="utf-8")
        self.stdout.write(f"  patched {path.relative_to(_PROJECT_ROOT)}")

    def _write_scope_urls(self, scope: str, *, force: bool) -> None:
        path = _PROJECT_PACKAGE_DIR / "api" / f"{scope}_urls.py"
        if path.exists() and not force:
            self.stdout.write(f"  skip existing {path.relative_to(_PROJECT_ROOT)}")
            return
        _write(
            path,
            f'''
"""Routes under ``/api/v1/{scope}/``."""

from django.urls import include, path

urlpatterns = [
    path("", include(("{_PROJECT_SLUG}.core.urls.{scope}_core_url", "{scope}_core"))),
    path("auth/", include(("{_PROJECT_SLUG}.users.urls.auth_url", "auth"))),
    path("users/", include(("{_PROJECT_SLUG}.users.urls.users_url", "users"))),
]
''',
        )
        self.stdout.write(f"  wrote {path.relative_to(_PROJECT_ROOT)}")

    def _write_scope_health(self, scope: str, pascal: str, *, force: bool) -> None:
        core_url = _PROJECT_PACKAGE_DIR / "core" / "urls" / f"{scope}_core_url.py"
        health = (
            _PROJECT_PACKAGE_DIR
            / "core"
            / "apis"
            / scope
            / "health"
            / f"{scope}_health_apis.py"
        )
        if core_url.exists() and health.exists() and not force:
            self.stdout.write("  skip existing health files")
            return
        _write(
            core_url,
            f'''
from django.urls import path

from {_PROJECT_SLUG}.core.apis.{scope}.health.{scope}_health_apis import {pascal}HealthApiView

app_name = "{scope}_core"

urlpatterns = [
    path("health/", {pascal}HealthApiView.as_view(), name="health"),
]
''',
        )
        _write(_PROJECT_PACKAGE_DIR / "core" / "apis" / scope / "__init__.py", "")
        _write(
            _PROJECT_PACKAGE_DIR / "core" / "apis" / scope / "health" / "__init__.py",
            f'from .{scope}_health_apis import {pascal}HealthApiView\n\n__all__ = ["{pascal}HealthApiView"]\n',
        )
        _write(
            health,
            f'''
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import AllowAny

from {_PROJECT_SLUG}.common.http.schema import envelope_serializer
from {_PROJECT_SLUG}.core.apis.health.health_apis import HealthApi


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
        self.stdout.write(f"  wrote health under core/apis/{scope}/")

    def _patch_api_urls(self, scope: str) -> None:
        path = _PROJECT_PACKAGE_DIR / "api" / "urls.py"
        text = path.read_text(encoding="utf-8")
        line = (
            f'    path("{scope}/", include(("{_PROJECT_SLUG}.api.{scope}_urls", "{scope}"))),'
        )
        if line in text:
            return
        idx = text.rfind("]")
        if idx < 0:
            raise CommandError(f"Could not patch {path}: unexpected format")
        text = text[:idx] + line + "\n" + text[idx:]
        path.write_text(text, encoding="utf-8")
        self.stdout.write(f"  patched {path.relative_to(_PROJECT_ROOT)}")

    def _patch_settings(self, scope: str, model_name: str) -> None:
        path = _PROJECT_ROOT / "config" / "settings" / "api_scopes.py"
        text = path.read_text(encoding="utf-8")
        scopes_block, _, rest = text.partition("API_SCOPE_USER_MODELS")
        if f'"{scope}"' not in scopes_block:
            text = text.replace(
                "API_SCOPES = [",
                f'API_SCOPES = [\n    "{scope}",',
                1,
            )
        map_line = f'    "{scope}": "users.{model_name}",'
        if map_line not in text:
            text = text.replace(
                "API_SCOPE_USER_MODELS = {",
                f"API_SCOPE_USER_MODELS = {{\n{map_line}",
                1,
            )
        path.write_text(text, encoding="utf-8")
        self.stdout.write(f"  patched {path.relative_to(_PROJECT_ROOT)}")

    def _patch_scope_registry(self, scope: str, model_name: str) -> None:
        path = _PROJECT_PACKAGE_DIR / "users" / "scope_registry.py"
        text = path.read_text(encoding="utf-8")
        map_line = f'    "{scope}": "users.{model_name}",'
        if map_line not in text:
            text = text.replace(
                "SCOPE_USER_MODEL_PATHS = {",
                f"SCOPE_USER_MODEL_PATHS = {{\n{map_line}",
                1,
            )
        path.write_text(text, encoding="utf-8")
        self.stdout.write(f"  patched {path.relative_to(_PROJECT_ROOT)}")

    def _patch_schema(self, scope: str, pascal: str) -> None:
        path = _PROJECT_PACKAGE_DIR / "common" / "http" / "schema.py"
        text = path.read_text(encoding="utf-8")
        line = f'{pascal}SchemaGenerator = make_scoped_schema_generator("/api/v1/{scope}")'
        if line not in text:
            path.write_text(text.rstrip() + f"\n{line}\n", encoding="utf-8")
            self.stdout.write(f"  patched {path.relative_to(_PROJECT_ROOT)}")

    def _patch_config_urls(self, scope: str, pascal: str) -> None:
        path = _PROJECT_ROOT / "config" / "urls.py"
        text = path.read_text(encoding="utf-8")
        import_token = f"{pascal}SchemaGenerator"
        if import_token not in text:
            text = re.sub(
                rf"(from {_PROJECT_SLUG}\.common\.http\.schema import )([^\n]+)",
                lambda m: m.group(0)
                if import_token in m.group(2)
                else f"{m.group(1)}{m.group(2)}, {import_token}",
                text,
                count=1,
            )
        if f'name="swagger-ui-{scope}"' not in text:
            block = f'''
        path(
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
            needle = 'name="redoc"),'
            if needle not in text:
                raise CommandError("Could not find docs urlpatterns to patch")
            text = text.replace(needle, needle + block, 1)
        path.write_text(text, encoding="utf-8")
        self.stdout.write(f"  patched {path.relative_to(_PROJECT_ROOT)}")

    def _patch_admin(self, scope: str, pascal: str, model_name: str) -> None:
        path = _PROJECT_PACKAGE_DIR / "users" / "admin.py"
        if not path.exists():
            return
        text = path.read_text(encoding="utf-8")
        if f"class {pascal}UserAdmin" in text:
            return
        text = re.sub(
            rf"from {_PROJECT_SLUG}\.users\.models import ([^\n]+)",
            lambda m: m.group(0)
            if model_name in m.group(1)
            else f"from {_PROJECT_SLUG}.users.models import {m.group(1)}, {model_name}",
            text,
            count=1,
        )
        text = (
            text.rstrip()
            + f"""

@admin.register({model_name})
class {pascal}UserAdmin(admin.ModelAdmin):
    search_fields = ("email",)
"""
        )
        path.write_text(text + "\n", encoding="utf-8")
        self.stdout.write(f"  patched {path.relative_to(_PROJECT_ROOT)}")

    def _write_migration(self, scope: str, model_name: str) -> None:
        mig_dir = _PROJECT_PACKAGE_DIR / "users" / "migrations"
        names = sorted(p.stem for p in mig_dir.glob("[0-9][0-9][0-9][0-9]_*.py"))
        dependency = names[-1] if names else "0001_initial"
        number = len(names) + 1
        label = scope.replace("_", " ")
        path = mig_dir / f"{number:04d}_{scope}_user.py"
        if path.exists():
            self.stdout.write(f"  skip existing {path.relative_to(_PROJECT_ROOT)}")
            return
        _write(
            path,
            f'''
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "{dependency}"),
    ]

    operations = [
        migrations.CreateModel(
            name="{model_name}",
            fields=[
                (
                    "baseuser_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={{
                "verbose_name": "{label} user",
                "verbose_name_plural": "{label} users",
            }},
            bases=("users.baseuser",),
        ),
    ]
''',
        )
        self.stdout.write(f"  wrote {path.relative_to(_PROJECT_ROOT)}")

    def _patch_scoped_rule(self, scope: str) -> None:
        path = _PROJECT_ROOT / ".cursor" / "rules" / "scoped-apis.mdc"
        if not path.exists():
            return
        text = path.read_text(encoding="utf-8")
        marker = "Enabled scopes: "
        line = next((ln for ln in text.splitlines() if ln.startswith(marker)), None)
        if not line:
            return
        listed = line[len(marker) :]
        token = f"`{scope}`"
        if token in listed:
            return
        if listed.endswith("."):
            new_line = f"{marker}{listed[:-1]}, {token}."
        else:
            new_line = f"{marker}{listed}, {token}"
        path.write_text(text.replace(line, new_line, 1), encoding="utf-8")
        self.stdout.write(f"  patched {path.relative_to(_PROJECT_ROOT)}")
