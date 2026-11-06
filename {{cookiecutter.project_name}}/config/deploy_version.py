"""Read the deploy version baked into the image (or present locally as version.txt)."""

from __future__ import annotations

from pathlib import Path

from config.env import BASE_DIR

VERSION_FILE_NAME = "version.txt"


def version_file_path() -> Path:
    return Path(str(BASE_DIR)) / VERSION_FILE_NAME


def read_deploy_version() -> str | None:
    """
    Return the trimmed contents of ``version.txt``, or ``None`` if missing/empty.

    Production images write this file from the Docker ``VERSION`` build-arg
    (CI tag or short SHA). Local/dev usually has no file → ``None``.
    """
    path = version_file_path()
    if not path.is_file():
        return None
    version = path.read_text(encoding="utf-8").strip()
    return version or None
