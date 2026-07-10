"""
Generic pure string validators for reuse across apps.

Rules:
- Name: is_*
- Return: bool only
- No exceptions, no translations, no domain messages
- Domain-specific checks (e.g. password) belong in <app>/validators/
"""

from __future__ import annotations

import re

_SLUG_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def is_non_empty(value: str) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_slug(value: str) -> bool:
    return isinstance(value, str) and _SLUG_RE.fullmatch(value) is not None
