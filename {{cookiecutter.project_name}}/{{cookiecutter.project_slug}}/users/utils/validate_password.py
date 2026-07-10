import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def number_validator(password):
    regex = re.compile("[0-9]")
    if regex.search(password) is None:
        raise ValidationError(_("password must include number"), code="password_must_include_number")


def letter_validator(password):
    regex = re.compile("[a-zA-Z]")
    if regex.search(password) is None:
        raise ValidationError(_("password must include letter"), code="password_must_include_letter")


def special_char_validator(password):
    regex = re.compile(r"[@_!#$%^&*()<>?/\|}{~:]")
    if regex.search(password) is None:
        raise ValidationError(_("password must include special char"), code="password_must_include_special_char")
