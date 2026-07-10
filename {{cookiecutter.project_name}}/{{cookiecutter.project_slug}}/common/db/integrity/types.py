from enum import Enum


class IntegrityErrorType(Enum):
    UNIQUE = "unique"
    NOT_NULL = "not_null"
    FOREIGN_KEY = "foreign_key"
    UNKNOWN = "unknown"
