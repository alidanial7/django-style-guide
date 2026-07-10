import re

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from {{cookiecutter.project_slug}}.users.errors.codes import UserErrorCode

# === Pure checks (is_* → bool, no exceptions) ===

_HAS_NUMBER_RE = re.compile(r"[0-9]")
_HAS_LETTER_RE = re.compile(r"[a-zA-Z]")
_HAS_SPECIAL_RE = re.compile(r"[@_!#$%^&*()<>?/\|}{~:]")


def is_password_with_number(value: str) -> bool:
    return isinstance(value, str) and _HAS_NUMBER_RE.search(value) is not None


def is_password_with_letter(value: str) -> bool:
    return isinstance(value, str) and _HAS_LETTER_RE.search(value) is not None


def is_password_with_special_char(value: str) -> bool:
    return isinstance(value, str) and _HAS_SPECIAL_RE.search(value) is not None


# === Raising field validators (*Validator → ValidationError) ===


@deconstructible
class PasswordNumberValidator:
    code = UserErrorCode.PASSWORD_MISSING_NUMBER
    message = _("password must include number")

    def __call__(self, value: str) -> None:
        if not is_password_with_number(value):
            raise ValidationError(self.message, code=self.code)


@deconstructible
class PasswordLetterValidator:
    code = UserErrorCode.PASSWORD_MISSING_LETTER
    message = _("password must include letter")

    def __call__(self, value: str) -> None:
        if not is_password_with_letter(value):
            raise ValidationError(self.message, code=self.code)


@deconstructible
class PasswordSpecialCharValidator:
    code = UserErrorCode.PASSWORD_MISSING_SPECIAL
    message = _("password must include special char")

    def __call__(self, value: str) -> None:
        if not is_password_with_special_char(value):
            raise ValidationError(self.message, code=self.code)


@deconstructible
class PasswordMinLengthValidator:
    code = UserErrorCode.PASSWORD_TOO_SHORT
    message = _("password must be at least %(limit_value)d characters")
    limit_value = 10

    def __call__(self, value: str) -> None:
        if not isinstance(value, str) or len(value) < self.limit_value:
            raise ValidationError(
                self.message,
                code=self.code,
                params={"limit_value": self.limit_value},
            )


validate_password_number = PasswordNumberValidator()
validate_password_letter = PasswordLetterValidator()
validate_password_special_char = PasswordSpecialCharValidator()
validate_password_min_length = PasswordMinLengthValidator()

PASSWORD_VALIDATORS = [
    validate_password_number,
    validate_password_letter,
    validate_password_special_char,
    validate_password_min_length,
]
