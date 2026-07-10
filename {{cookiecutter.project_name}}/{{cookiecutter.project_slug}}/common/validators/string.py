"""
Generic pure string validators for reuse across apps.

Rules:
- Name: is_*
- Return: bool only
- No exceptions, no translations, no domain messages
- Domain-specific checks (e.g. password) belong in <app>/validators/

Example (uncomment / copy when needed):

    import re

    _SLUG_RE = re.compile(r"^[a-z0-9_]+$")

    def is_slug(value: str) -> bool:
        return isinstance(value, str) and _SLUG_RE.fullmatch(value) is not None
"""

# Keep this module import-safe even if no live helpers exist yet.
