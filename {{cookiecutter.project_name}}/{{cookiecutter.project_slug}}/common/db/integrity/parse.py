from __future__ import annotations

import re
from dataclasses import dataclass

from django.db import IntegrityError
from django.db.models import Model

from .types import IntegrityErrorType

# PostgreSQL SQLSTATE codes
_PG_UNIQUE = "23505"
_PG_NOT_NULL = "23502"
_PG_FOREIGN_KEY = "23503"

_SQLITE_UNIQUE_RE = re.compile(r"UNIQUE constraint failed:\s*([\w.]+)", re.IGNORECASE)
_SQLITE_NOT_NULL_RE = re.compile(r"NOT NULL constraint failed:\s*([\w.]+)", re.IGNORECASE)
_PG_DETAIL_KEY_RE = re.compile(r"Key \((?P<columns>[^)]+)\)=", re.IGNORECASE)
_PG_COLUMN_RE = re.compile(r'column "(?P<column>[^"]+)"', re.IGNORECASE)


@dataclass(frozen=True)
class ParsedIntegrityError:
    error_type: IntegrityErrorType
    columns: tuple[str, ...] = ()


def _pgcode(error: IntegrityError) -> str | None:
    cause = getattr(error, "__cause__", None)
    if cause is None:
        return None
    return getattr(cause, "pgcode", None) or getattr(cause, "sqlstate", None)


def _message(error: IntegrityError) -> str:
    parts = [str(error)]
    cause = getattr(error, "__cause__", None)
    if cause is not None:
        parts.append(str(cause))
        diag = getattr(cause, "diag", None)
        if diag is not None:
            for attr in ("message_primary", "message_detail", "constraint_name"):
                value = getattr(diag, attr, None)
                if value:
                    parts.append(str(value))
    return "\n".join(parts)


def _columns_from_table_dot_column(raw: str) -> tuple[str, ...]:
    columns: list[str] = []
    for part in raw.split(","):
        part = part.strip()
        if "." in part:
            part = part.rsplit(".", 1)[-1]
        if part:
            columns.append(part)
    return tuple(columns)


def _map_columns_to_fields(model: type[Model], columns: tuple[str, ...]) -> tuple[str, ...]:
    field_by_column = {field.column: field.name for field in model._meta.local_fields}
    mapped: list[str] = []
    for column in columns:
        mapped.append(field_by_column.get(column, column))
    return tuple(mapped)


def parse_integrity_error(error: IntegrityError, *, model: type[Model]) -> ParsedIntegrityError:
    pgcode = _pgcode(error)
    message = _message(error)

    if pgcode == _PG_UNIQUE:
        match = _PG_DETAIL_KEY_RE.search(message)
        columns = tuple(part.strip() for part in match.group("columns").split(",")) if match else ()
        return ParsedIntegrityError(IntegrityErrorType.UNIQUE, _map_columns_to_fields(model, columns))

    if pgcode == _PG_NOT_NULL:
        match = _PG_COLUMN_RE.search(message)
        columns = (match.group("column"),) if match else ()
        return ParsedIntegrityError(IntegrityErrorType.NOT_NULL, _map_columns_to_fields(model, columns))

    if pgcode == _PG_FOREIGN_KEY:
        match = _PG_DETAIL_KEY_RE.search(message) or _PG_COLUMN_RE.search(message)
        if match and "columns" in match.groupdict() and match.group("columns"):
            columns = tuple(part.strip() for part in match.group("columns").split(","))
        elif match and "column" in match.groupdict():
            columns = (match.group("column"),)
        else:
            columns = ()
        return ParsedIntegrityError(IntegrityErrorType.FOREIGN_KEY, _map_columns_to_fields(model, columns))

    unique_match = _SQLITE_UNIQUE_RE.search(message)
    if unique_match:
        columns = _columns_from_table_dot_column(unique_match.group(1))
        return ParsedIntegrityError(IntegrityErrorType.UNIQUE, _map_columns_to_fields(model, columns))

    not_null_match = _SQLITE_NOT_NULL_RE.search(message)
    if not_null_match:
        columns = _columns_from_table_dot_column(not_null_match.group(1))
        return ParsedIntegrityError(IntegrityErrorType.NOT_NULL, _map_columns_to_fields(model, columns))

    return ParsedIntegrityError(IntegrityErrorType.UNKNOWN)
