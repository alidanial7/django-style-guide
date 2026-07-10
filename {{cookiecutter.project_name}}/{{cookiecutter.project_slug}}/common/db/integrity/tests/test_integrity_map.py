import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework.exceptions import APIException

from {{cookiecutter.project_slug}}.common.db.integrity import (
    IntegrityErrorType,
    map_integrity_error,
    parse_integrity_error,
)
from {{cookiecutter.project_slug}}.common.errors.codes import ErrorCode
from {{cookiecutter.project_slug}}.users.models import BaseUser


class _PgCause(Exception):
    """Minimal stand-in for a psycopg DatabaseError with pgcode + diag."""

    def __init__(self, pgcode: str, detail: str = ""):
        self.pgcode = pgcode
        self.diag = type(
            "Diag",
            (),
            {"message_detail": detail, "message_primary": "", "constraint_name": ""},
        )()
        super().__init__(detail or f"pgcode={pgcode}")


def _integrity_with_pgcode(pgcode: str, detail: str = "") -> IntegrityError:
    error = IntegrityError("db integrity error")
    error.__cause__ = _PgCause(pgcode, detail)
    return error


def test_parse_sqlite_unique_violation():
    error = IntegrityError("UNIQUE constraint failed: users_baseuser.email")
    parsed = parse_integrity_error(error, model=BaseUser)
    assert parsed.error_type == IntegrityErrorType.UNIQUE
    assert parsed.columns == ("email",)


def test_parse_sqlite_not_null_violation():
    error = IntegrityError("NOT NULL constraint failed: users_baseuser.email")
    parsed = parse_integrity_error(error, model=BaseUser)
    assert parsed.error_type == IntegrityErrorType.NOT_NULL
    assert parsed.columns == ("email",)


def test_parse_postgres_unique_pgcode():
    error = _integrity_with_pgcode("23505", "Key (email)=(a@b.com) already exists.")
    parsed = parse_integrity_error(error, model=BaseUser)
    assert parsed.error_type == IntegrityErrorType.UNIQUE
    assert parsed.columns == ("email",)


def test_parse_postgres_not_null_pgcode():
    error = _integrity_with_pgcode("23502", 'null value in column "email" violates not-null constraint')
    parsed = parse_integrity_error(error, model=BaseUser)
    assert parsed.error_type == IntegrityErrorType.NOT_NULL
    assert parsed.columns == ("email",)


def test_parse_postgres_fk_pgcode():
    error = _integrity_with_pgcode("23503", "Key (user_id)=(1) is not present in table")
    parsed = parse_integrity_error(error, model=BaseUser)
    assert parsed.error_type == IntegrityErrorType.FOREIGN_KEY


def test_map_unique_raises_field_validation_error():
    error = IntegrityError("UNIQUE constraint failed: users_baseuser.email")
    with pytest.raises(ValidationError) as exc_info:
        map_integrity_error(error, model=BaseUser)
    assert "email" in exc_info.value.message_dict
    assert exc_info.value.error_dict["email"][0].code == ErrorCode.UNIQUE


def test_map_not_null_uses_not_null_code():
    error = IntegrityError("NOT NULL constraint failed: users_baseuser.email")
    with pytest.raises(ValidationError) as exc_info:
        map_integrity_error(error, model=BaseUser)
    assert exc_info.value.error_dict["email"][0].code == ErrorCode.NOT_NULL


def test_map_unknown_raises_api_exception():
    error = IntegrityError("something unexpected")
    with pytest.raises(APIException) as exc_info:
        map_integrity_error(error, model=BaseUser)
    assert exc_info.value.get_codes() == ErrorCode.UNKNOWN_INTEGRITY
