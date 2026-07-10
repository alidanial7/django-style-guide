import pytest
from django.core.exceptions import ValidationError

from {{cookiecutter.project_slug}}.users.errors.codes import UserErrorCode
from {{cookiecutter.project_slug}}.users.validators.password import (
    is_password_with_letter,
    is_password_with_number,
    is_password_with_special_char,
    validate_password_letter,
    validate_password_min_length,
    validate_password_number,
    validate_password_special_char,
)


@pytest.mark.parametrize(
    ("func", "value", "expected"),
    [
        (is_password_with_number, "abc1", True),
        (is_password_with_number, "abcdef", False),
        (is_password_with_letter, "123a", True),
        (is_password_with_letter, "12345", False),
        (is_password_with_special_char, "abc!", True),
        (is_password_with_special_char, "abcdef", False),
        (is_password_with_number, None, False),
    ],
)
def test_pure_password_validators(func, value, expected):
    assert func(value) is expected


@pytest.mark.parametrize(
    ("validator", "value", "code"),
    [
        (validate_password_number, "Password!", UserErrorCode.PASSWORD_MISSING_NUMBER),
        (validate_password_letter, "1234567890!", UserErrorCode.PASSWORD_MISSING_LETTER),
        (validate_password_special_char, "Password1", UserErrorCode.PASSWORD_MISSING_SPECIAL),
        (validate_password_min_length, "short", UserErrorCode.PASSWORD_TOO_SHORT),
    ],
)
def test_raising_password_validators(validator, value, code):
    with pytest.raises(ValidationError) as exc_info:
        validator(value)
    assert exc_info.value.code == code
