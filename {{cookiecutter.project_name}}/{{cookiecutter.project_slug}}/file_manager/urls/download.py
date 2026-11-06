"""Resolve download URL paths for managed files (scoped or flat mounts)."""

from __future__ import annotations

from typing import Any


def managed_file_download_path(*, file_id: Any, request: Any | None = None) -> str:
    """Return the URL path for ``files-download``.

    Multi-scope mounts live at ``/api/v1/<scope>/files/…``
    (``api:<scope>:file_manager:files-download``). Flat mounts stay at
    ``/api/v1/files/…`` (``api:file_manager:files-download``).
    """
    scope = getattr(request, "api_scope", None) if request is not None else None
    if scope:
        name = f"api:{scope}:file_manager:files-download"
        fallback = f"/api/v1/{scope}/files/{file_id}/download/"
    else:
        name = "api:file_manager:files-download"
        fallback = f"/api/v1/files/{file_id}/download/"
    try:
        from django.urls import reverse

        return reverse(name, kwargs={"file_id": file_id})
    except Exception:
        return fallback
