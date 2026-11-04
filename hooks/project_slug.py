"""Shared project_slug normalization for prompts and pre_gen validation.

Named ``project_slug`` (not ``slugify``) so it does not shadow the
``python-slugify`` package Cookiecutter loads as a Jinja extension.
"""

from __future__ import annotations

import re

_SLUG_RE = re.compile(r"^[_a-zA-Z][_a-zA-Z0-9]+$")


def slugify(value: str) -> str:
    slug = value.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    return slug.strip("_")


def is_valid_project_slug(value: str) -> bool:
    return bool(_SLUG_RE.match(value))
