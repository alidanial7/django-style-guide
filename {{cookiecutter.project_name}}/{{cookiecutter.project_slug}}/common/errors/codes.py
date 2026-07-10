from enum import StrEnum


class ErrorCode(StrEnum):
    """Platform-only machine codes (integrity + shared input). No domain codes here."""

    INVALID_FORMAT = "invalid_format"
    INVALID = "invalid"  # fallback when a raiser did not set code=
    REQUIRED = "required"
    NOT_NULL = "not_null"
    UNIQUE = "unique"
    INVALID_REFERENCE = "invalid_reference"
    UNKNOWN_INTEGRITY = "integrity_error"
    APPLICATION_ERROR = "application_error"
    SERVER_ERROR = "server_error"
