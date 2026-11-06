from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from {{cookiecutter.project_slug}}.users.errors.codes import UserErrorCode

# Stored format: IR mobile with country code, digits only (e.g. 989134543456).
_IRAN_MOBILE_RE = re.compile(r"^989\d{9}$")


def normalize_phone(*, raw: str) -> str:
    """
    Normalize user input to ``98XXXXXXXXXX`` (no ``+``, no leading ``0``).

    Accepts common Iranian forms: ``0913…``, ``913…``, ``+98913…``, ``98913…``.
    """
    digits = re.sub(r"\D", "", (raw or "").strip())
    if digits.startswith("0098"):
        digits = digits[2:]
    if digits.startswith("0") and len(digits) == 11:
        digits = "98" + digits[1:]
    elif len(digits) == 10 and digits.startswith("9"):
        digits = "98" + digits
    return digits


def validate_phone(*, phone: str) -> str:
    """Normalize then validate; raise ``ValidationError`` with ``UserErrorCode``."""
    normalized = normalize_phone(raw=phone)
    if not _IRAN_MOBILE_RE.match(normalized):
        raise ValidationError(
            _("Enter a valid mobile number (e.g. 989134543456)."),
            code=UserErrorCode.INVALID_PHONE,
        )
    return normalized
