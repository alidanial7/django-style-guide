from enum import StrEnum


class FileManagerErrorCode(StrEnum):
    """Domain machine codes for file_manager."""

    FILE_NOT_FOUND = "file_not_found"
    FILE_TOO_LARGE = "file_too_large"
    FILE_EMPTY = "file_empty"
    INVALID_FILE_TYPE = "invalid_file_type"
    INVALID_MIME_TYPE = "invalid_mime_type"
    FILE_ACCESS_DENIED = "file_access_denied"
    FILE_UPLOAD_FAILED = "file_upload_failed"
