"""Parse / validate API scope names for the cookiecutter wizard and hooks."""

from __future__ import annotations

import re

SCOPE_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
# ``admin`` is allowed as an API scope (mounted at /api/v1/admin/, not Django /admin/).
RESERVED_SCOPES_BLOCK = frozenset(
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


def parse_api_scopes(raw: str) -> list[str]:
    """Split a comma-separated scope list into normalized names."""
    scopes: list[str] = []
    seen: set[str] = set()
    for part in (raw or "").split(","):
        name = part.strip().lower()
        if not name:
            continue
        if name in seen:
            continue
        seen.add(name)
        scopes.append(name)
    return scopes


def validate_api_scopes(scopes: list[str]) -> None:
    """Raise ValueError if scope list is empty or any name is invalid."""
    if not scopes:
        raise ValueError(
            "api_scopes must list at least one scope "
            "(e.g. admin,factory,customer)."
        )
    for name in scopes:
        if not SCOPE_NAME_RE.match(name):
            raise ValueError(
                f"Invalid scope {name!r}. Use lowercase English letters, "
                "digits, underscore; must start with a letter; no spaces "
                "(e.g. admin, factory, customer)."
            )
        if name in RESERVED_SCOPES_BLOCK:
            raise ValueError(
                f"Scope {name!r} is reserved for platform routes. "
                "Pick another name."
            )


def scope_pascal(scope: str) -> str:
    """admin → Admin, content_team → ContentTeam."""
    return "".join(part.capitalize() for part in scope.split("_") if part)


def scopes_from_cookiecutter(raw: str) -> list[str]:
    scopes = parse_api_scopes(raw)
    validate_api_scopes(scopes)
    return scopes
