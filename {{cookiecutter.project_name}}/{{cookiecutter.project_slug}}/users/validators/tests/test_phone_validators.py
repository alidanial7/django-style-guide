import pytest
from django.core.exceptions import ValidationError

from {{cookiecutter.project_slug}}.users.errors.codes import UserErrorCode
from {{cookiecutter.project_slug}}.users.validators.phone import normalize_phone, validate_phone


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("989134543456", "989134543456"),
        ("+98 913 454 3456", "989134543456"),
        ("09134543456", "989134543456"),
        ("9134543456", "989134543456"),
    ],
)
def test_normalize_phone(raw: str, expected: str):
    assert normalize_phone(raw=raw) == expected


def test_validate_phone_accepts_iran_mobile():
    assert validate_phone(phone="09134543456") == "989134543456"


def test_validate_phone_rejects_invalid():
    with pytest.raises(ValidationError) as exc:
        validate_phone(phone="02112345678")
    assert exc.value.code == UserErrorCode.INVALID_PHONE
