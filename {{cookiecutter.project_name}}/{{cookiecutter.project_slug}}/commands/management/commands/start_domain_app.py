from __future__ import annotations

import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

# project_slug/commands/management/commands/start_domain_app.py
_COMMANDS_APP_DIR = Path(__file__).resolve().parents[2]
_PROJECT_PACKAGE_DIR = _COMMANDS_APP_DIR.parent
_PROJECT_ROOT = _PROJECT_PACKAGE_DIR.parent
_PROJECT_SLUG = _PROJECT_PACKAGE_DIR.name

_APP_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_RESERVED = frozenset(
    {
        "api",
        "common",
        "commands",
        "config",
        "core",
        "django",
        "manage",
        "test",
        "tests",
    }
)


# Placeholders use __NAME__ so Cookiecutter/Jinja does not rewrite this file.
def _to_pascal(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_") if part)


def _render(template: str, context: dict[str, str]) -> str:
    result = template
    # Replace longest keys first so __APP_NAME__ is not eaten by a greedy regex.
    for key in sorted(context.keys(), key=len, reverse=True):
        result = result.replace(f"__{key.upper()}__", context[key])
    return result


def _testing_enabled() -> bool:
    """True when the project was generated with testing (pytest.ini present)."""
    return (_PROJECT_ROOT / "pytest.ini").is_file()


_FILES: dict[str, str] = {
    "__init__.py": "",
    "apps.py": """from django.apps import AppConfig


class __APP_CONFIG__(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "__PROJECT_SLUG__.__APP_NAME__"
""",
    "admin.py": """from django.contrib import admin

# Register your models here.
""",
    "constants.py": '''"""App-level constants for __APP_NAME__."""
''',
    "models/__init__.py": """# from .example import Example
#
# __all__ = ["Example"]
""",
    "manager/__init__.py": "",
    "selector/__init__.py": """# from .__APP_NAME___selectors import ...
#
# __all__ = []
""",
    "services/__init__.py": """# from .__APP_NAME___services import ...
#
# __all__ = []
""",
    "apis/__init__.py": "",
    "urls/__init__.py": "",
    "urls/__APP_NAME__.py": """from django.urls import path

app_name = "__APP_NAME__"

urlpatterns = [
    # path("", SomeApi.as_view(), name="list"),
]
""",
    "validators/__init__.py": '''"""Domain validators for __APP_NAME__ (is_* pures + *Validator raisers)."""
''',
    "errors/__init__.py": """from .codes import __ERROR_CODE_CLASS__

__all__ = ["__ERROR_CODE_CLASS__"]
""",
    "errors/codes.py": '''from enum import StrEnum


class __ERROR_CODE_CLASS__(StrEnum):
    """Domain machine codes for __APP_NAME__. Add codes as features grow."""

    # EXAMPLE = "example"
''',
    "signals/__init__.py": "",
    "utils/__init__.py": "",
    "migrations/__init__.py": "",
}

# Created only when pytest.ini exists (project generated with testing).
_TEST_FILES: dict[str, str] = {
    "tests/__init__.py": "",
    "tests/test_app.py": """import pytest

from __PROJECT_SLUG__.__APP_NAME__.apps import __APP_CONFIG__


@pytest.mark.django_db
class Test__APP_CLASS__App:
    def test_app_config_is_importable(self):
        assert __APP_CONFIG__.name == "__PROJECT_SLUG__.__APP_NAME__"
""",
    "tests/__APP_NAME___factories.py": """# import factory
#
# from __PROJECT_SLUG__.__APP_NAME__.models import Example
#
#
# class ExampleFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = Example
#
#     name = factory.Sequence(lambda n: f"example-{n}")
""",
    "services/tests/__init__.py": "",
    "services/tests/test___APP_NAME___services.py": '''import pytest


@pytest.mark.django_db
class Test__APP_CLASS__Services:
    """Add service tests as you implement __PROJECT_SLUG__.__APP_NAME__.services."""

    def test_placeholder_ready_for_services(self):
        assert True
''',
    "selector/tests/__init__.py": "",
    "selector/tests/test___APP_NAME___selectors.py": '''import pytest


@pytest.mark.django_db
class Test__APP_CLASS__Selectors:
    """Add selector tests as you implement __PROJECT_SLUG__.__APP_NAME__.selector."""

    def test_placeholder_ready_for_selectors(self):
        assert True
''',
    "apis/tests/__init__.py": "",
    "apis/tests/test___APP_NAME___apis.py": '''import pytest


@pytest.mark.django_db
class Test__APP_CLASS__Apis:
    """Add API tests under feature folders (see users/apis/.../tests/) as endpoints land."""

    def test_placeholder_ready_for_apis(self):
        assert True
''',
    "validators/tests/__init__.py": "",
}


class Command(BaseCommand):
    help = (
        "Create a domain app with this project's style-guide layout "
        "(models/, services/, selector/, apis/, validators/, errors/, …). "
        "When testing is enabled (pytest.ini), also scaffolds base test stubs. "
        "Prefer this over Django's default startapp."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "name",
            type=str,
            help="Plural app label (Python package), e.g. blogs or order_items — prefer plural like users",
        )
        parser.add_argument(
            "--register",
            action="store_true",
            help="Append the new AppConfig to config/settings/apps.py LOCAL_APPS",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing scaffold files in the app directory (use with care)",
        )
        parser.add_argument(
            "--no-tests",
            action="store_true",
            help="Skip test stubs even if the project has pytest.ini",
        )

    def handle(self, *args, **options):
        app_name: str = options["name"].strip()
        register: bool = options["register"]
        force: bool = options["force"]
        no_tests: bool = options["no_tests"]

        if not _APP_NAME_RE.match(app_name):
            raise CommandError(
                "App name must be a lowercase Python identifier (start with a letter; only a-z, 0-9, underscore)."
            )
        if app_name in _RESERVED:
            raise CommandError(f"'{app_name}' is reserved in this template.")

        app_dir = _PROJECT_PACKAGE_DIR / app_name
        if app_dir.exists() and any(app_dir.iterdir()) and not force:
            raise CommandError(
                f"Directory already exists and is not empty: {app_dir}\n"
                "Use --force to overwrite scaffold files, or choose another name."
            )

        pascal = _to_pascal(app_name)
        context = {
            "app_name": app_name,
            "app_class": pascal,
            "app_config": f"{pascal}Config",
            "error_code_class": f"{pascal}ErrorCode",
            "project_slug": _PROJECT_SLUG,
        }

        files = dict(_FILES)
        include_tests = _testing_enabled() and not no_tests
        if include_tests:
            files.update(_TEST_FILES)
        elif _testing_enabled() and no_tests:
            self.stdout.write(self.style.WARNING("Skipping test stubs (--no-tests)."))
        elif not _testing_enabled():
            self.stdout.write(self.style.NOTICE("Testing not detected (no pytest.ini) — skipping test stubs."))

        created: list[str] = []
        for relative, template in files.items():
            path = app_dir / _render(relative, context)
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists() and not force:
                continue
            path.write_text(_render(template, context), encoding="utf-8")
            created.append(str(path.relative_to(_PROJECT_ROOT)))

        if not created and not force:
            self.stdout.write(self.style.WARNING("Nothing to create (files already present)."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Created domain app '{app_name}' with {len(created)} file(s)."))
            for item in created:
                self.stdout.write(f"  + {item}")
            if include_tests:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Base tests included (pytest.ini found). Run: pytest {_PROJECT_SLUG}/{app_name} -q"
                    )
                )

        config_path = f"{_PROJECT_SLUG}.{app_name}.apps.{context['app_config']}"
        if register:
            self._register_local_app(config_path, app_name)
        else:
            self.stdout.write("")
            self.stdout.write("Next steps:")
            self.stdout.write("  1. Add to LOCAL_APPS in config/settings/apps.py:")
            self.stdout.write(f'       "{config_path}",')
            self.stdout.write(f"     Or re-run with: python manage.py start_domain_app {app_name} --register")
            self.stdout.write(f"  2. Wire URLs in {_PROJECT_SLUG}/api/urls.py, e.g.:")
            self.stdout.write(
                f'       path("{app_name}/", include(("{_PROJECT_SLUG}.{app_name}.urls.{app_name}", "{app_name}"))),'
            )
            self.stdout.write(f"  3. Add models under {_PROJECT_SLUG}/{app_name}/models/, then makemigrations.")

    def _register_local_app(self, config_path: str, app_name: str) -> None:
        apps_file = _PROJECT_ROOT / "config" / "settings" / "apps.py"
        if not apps_file.is_file():
            raise CommandError(f"Could not find {apps_file}")

        text = apps_file.read_text(encoding="utf-8")
        entry = f'    "{config_path}",\n'

        if config_path in text:
            self.stdout.write(self.style.WARNING(f"Already registered in LOCAL_APPS: {config_path}"))
            return

        match = re.search(r"(LOCAL_APPS\s*=\s*\[)(.*?)(\n\])", text, flags=re.DOTALL)
        if not match:
            raise CommandError(f"Could not locate LOCAL_APPS list in {apps_file}")

        body = match.group(2)
        if body and not body.endswith("\n"):
            body += "\n"
        new_text = text[: match.start(2)] + body + entry + text[match.start(3) :]
        apps_file.write_text(new_text, encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Registered in LOCAL_APPS: {config_path}"))
        self.stdout.write("")
        self.stdout.write("Still needed:")
        self.stdout.write(f"  - Wire URLs in {_PROJECT_SLUG}/api/urls.py")
        self.stdout.write(
            f'      path("{app_name}/", include(("{_PROJECT_SLUG}.{app_name}.urls.{app_name}", "{app_name}"))),'
        )
        self.stdout.write(f"  - Add models under {_PROJECT_SLUG}/{app_name}/models/, then makemigrations")
