import os

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from {{cookiecutter.project_slug}}.file_manager.constants import (
    ALLOWED_FILE_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    MAX_FILE_SIZE,
    get_category_rule,
)
from {{cookiecutter.project_slug}}.file_manager.errors.codes import FileManagerErrorCode


def is_valid_file_size(*, size: int, max_size: int = MAX_FILE_SIZE) -> bool:
    return 0 < size <= max_size


def is_valid_file_extension(
    *,
    filename: str,
    allowed_extensions: list[str] | tuple[str, ...] = ALLOWED_FILE_EXTENSIONS,
) -> bool:
    ext = os.path.splitext(filename)[1].lstrip(".").lower()
    return ext in [e.lower() for e in allowed_extensions]


def is_valid_file_mime_type(
    *,
    mime_type: str | None,
    allowed_mime_types: list[str] | tuple[str, ...] = ALLOWED_MIME_TYPES,
) -> bool:
    if not mime_type:
        return True
    return mime_type.lower() in [m.lower() for m in allowed_mime_types]


@deconstructible
class FileSizeValidator:
    message = _("file size cannot exceed %(max_size)d mb.")
    empty_message = _("file cannot be empty.")
    code = FileManagerErrorCode.FILE_TOO_LARGE

    def __init__(self, max_size: int = MAX_FILE_SIZE) -> None:
        self.max_size = max_size

    def __call__(self, file: UploadedFile) -> None:
        if file.size is not None and file.size <= 0:
            raise ValidationError(
                self.empty_message,
                code=FileManagerErrorCode.FILE_EMPTY,
            )
        if not is_valid_file_size(size=file.size or 0, max_size=self.max_size):
            max_size_mb = self.max_size // (1024 * 1024)
            raise ValidationError(
                self.message,
                code=self.code,
                params={"max_size": max_size_mb},
            )


@deconstructible
class FileExtensionValidator:
    message = _("file extension .%(ext)s is not allowed. allowed extensions: %(allowed)s.")
    code = FileManagerErrorCode.INVALID_FILE_TYPE

    def __init__(
        self,
        allowed_extensions: list[str] | tuple[str, ...] = ALLOWED_FILE_EXTENSIONS,
    ) -> None:
        self.allowed_extensions = allowed_extensions

    def __call__(self, file: UploadedFile) -> None:
        if not is_valid_file_extension(
            filename=file.name or "",
            allowed_extensions=self.allowed_extensions,
        ):
            ext = os.path.splitext(file.name or "")[1].lstrip(".").lower()
            raise ValidationError(
                self.message,
                code=self.code,
                params={
                    "ext": ext,
                    "allowed": ", ".join(self.allowed_extensions),
                },
            )


@deconstructible
class FileMimeTypeValidator:
    message = _("file content type (%(content_type)s) is not allowed.")
    code = FileManagerErrorCode.INVALID_MIME_TYPE

    def __init__(
        self,
        allowed_mime_types: list[str] | tuple[str, ...] = ALLOWED_MIME_TYPES,
    ) -> None:
        self.allowed_mime_types = allowed_mime_types

    def __call__(self, file: UploadedFile) -> None:
        content_type = getattr(file, "content_type", None)
        if content_type and not is_valid_file_mime_type(
            mime_type=content_type,
            allowed_mime_types=self.allowed_mime_types,
        ):
            raise ValidationError(
                self.message,
                code=self.code,
                params={"content_type": content_type},
            )


validate_file_size = FileSizeValidator()
validate_file_extension = FileExtensionValidator()
validate_file_mime_type = FileMimeTypeValidator()


def validate_managed_file(file: UploadedFile, *, category: str | None = None) -> None:
    """Validate size, extension, and MIME type for an upload (optionally by category)."""
    rule = get_category_rule(category)
    FileSizeValidator(max_size=rule.get("max_size", MAX_FILE_SIZE))(file)
    FileExtensionValidator(
        allowed_extensions=rule.get("allowed_extensions", ALLOWED_FILE_EXTENSIONS)
    )(file)
    FileMimeTypeValidator(
        allowed_mime_types=rule.get("allowed_mime_types", ALLOWED_MIME_TYPES)
    )(file)
