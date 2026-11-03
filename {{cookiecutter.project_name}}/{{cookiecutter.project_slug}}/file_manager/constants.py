from typing import TypedDict

from {{cookiecutter.project_slug}}.file_manager.enums import FileCategory

FILE_MANAGER_TAGS = ["File Manager"]

DEFAULT_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
DEFAULT_ALLOWED_FILE_EXTENSIONS = ["jpg", "jpeg", "png", "pdf", "xlsx", "csv"]
DEFAULT_ALLOWED_MIME_TYPES = [
    "image/jpeg",
    "image/png",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv",
    "text/plain",
    "application/csv",
]
DEFAULT_IS_PUBLIC = False

MAX_FILE_SIZE = DEFAULT_MAX_FILE_SIZE
ALLOWED_MIME_TYPES = DEFAULT_ALLOWED_MIME_TYPES
ALLOWED_FILE_EXTENSIONS = DEFAULT_ALLOWED_FILE_EXTENSIONS

PROTECTED_STORAGE_URL = "/protected/"


class FileCategoryRule(TypedDict, total=False):
    is_public: bool
    max_size: int
    allowed_extensions: list[str]
    allowed_mime_types: list[str]


CATEGORY_FILE_RULES: dict[str, FileCategoryRule] = {
    FileCategory.AVATAR: {
        "is_public": True,
        "max_size": 5 * 1024 * 1024,
        "allowed_extensions": ["jpg", "jpeg", "png"],
        "allowed_mime_types": ["image/jpeg", "image/png"],
    },
    FileCategory.IMAGE: {
        "is_public": False,
        "max_size": 10 * 1024 * 1024,
        "allowed_extensions": ["jpg", "jpeg", "png"],
        "allowed_mime_types": ["image/jpeg", "image/png"],
    },
    FileCategory.DOCUMENT: {
        "is_public": False,
        "max_size": 10 * 1024 * 1024,
        "allowed_extensions": ["pdf", "jpg", "jpeg", "png", "xlsx", "csv"],
        "allowed_mime_types": [
            "application/pdf",
            "image/jpeg",
            "image/png",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/csv",
            "text/plain",
            "application/csv",
        ],
    },
    FileCategory.OTHER: {
        "is_public": False,
        "max_size": DEFAULT_MAX_FILE_SIZE,
        "allowed_extensions": DEFAULT_ALLOWED_FILE_EXTENSIONS,
        "allowed_mime_types": DEFAULT_ALLOWED_MIME_TYPES,
    },
}


def get_category_rule(category: str | None = None) -> FileCategoryRule:
    """Return size/extension/mime/publicity rules for a category."""
    if not category or category not in CATEGORY_FILE_RULES:
        return {
            "is_public": DEFAULT_IS_PUBLIC,
            "max_size": DEFAULT_MAX_FILE_SIZE,
            "allowed_extensions": DEFAULT_ALLOWED_FILE_EXTENSIONS,
            "allowed_mime_types": DEFAULT_ALLOWED_MIME_TYPES,
        }
    rule = CATEGORY_FILE_RULES[category]
    return {
        "is_public": rule.get("is_public", DEFAULT_IS_PUBLIC),
        "max_size": rule.get("max_size", DEFAULT_MAX_FILE_SIZE),
        "allowed_extensions": rule.get("allowed_extensions", DEFAULT_ALLOWED_FILE_EXTENSIONS),
        "allowed_mime_types": rule.get("allowed_mime_types", DEFAULT_ALLOWED_MIME_TYPES),
    }


def is_category_public(category: str | None = None) -> bool:
    """Whether the category defaults to public downloads."""
    return bool(get_category_rule(category).get("is_public", DEFAULT_IS_PUBLIC))
