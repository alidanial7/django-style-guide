from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.http import FileResponse, Http404, HttpResponse
from django.utils.http import content_disposition_header
from django.utils.translation import gettext_lazy as _

from {{cookiecutter.project_slug}}.common import services as common_services
from {{cookiecutter.project_slug}}.common.services import model_create
from {{cookiecutter.project_slug}}.file_manager.constants import PROTECTED_STORAGE_URL, is_category_public
from {{cookiecutter.project_slug}}.file_manager.enums import FileCategory
from {{cookiecutter.project_slug}}.file_manager.models import ManagedFile
from {{cookiecutter.project_slug}}.file_manager.types import CreateManagedFileData
from {{cookiecutter.project_slug}}.file_manager.validators import validate_managed_file
from {{cookiecutter.project_slug}}.users.models import BaseUser


@transaction.atomic
def create_managed_file(
    *,
    user: BaseUser,
    data: CreateManagedFileData | None = None,
    file_obj: UploadedFile | None = None,
    title: str | None = None,
    category: str = FileCategory.OTHER,
    is_public: bool | None = None,
) -> ManagedFile:
    """Validate and persist an uploaded file owned by ``user``."""
    if data is not None:
        file_obj = data["file"]
        title = data.get("title", title)
        category = data.get("category", category)
        is_public = data.get("is_public", is_public)
    elif file_obj is None:
        raise ValueError("Either 'data' or 'file_obj' must be provided to create_managed_file.")

    if is_public is None:
        is_public = is_category_public(category)

    validate_managed_file(file_obj, category=category)

    original_filename = file_obj.name or "unnamed_file"
    file_title = title.strip() if title else original_filename

    return model_create(
        model_class=ManagedFile,
        data={
            "title": file_title,
            "original_filename": original_filename,
            "file": file_obj,
            "file_size": file_obj.size,
            "mime_type": getattr(file_obj, "content_type", "") or "application/octet-stream",
            "category": category,
            "is_public": is_public,
            "owner": user,
        },
    )


@transaction.atomic
def delete_managed_file(*, managed_file: ManagedFile) -> None:
    """Delete the DB row; physical cleanup is handled by the post_delete signal."""
    if hasattr(common_services, "model_delete"):
        common_services.model_delete(instance=managed_file)
    else:
        managed_file.delete()


def serve_managed_file_securely(*, managed_file: ManagedFile) -> HttpResponse | FileResponse:
    """Serve file bytes via FileResponse in DEBUG, or Nginx X-Accel-Redirect in production."""
    if not managed_file.file:
        raise Http404(_("file content not found."))

    content_type = managed_file.mime_type or "application/octet-stream"
    disposition = content_disposition_header(
        as_attachment=False,
        filename=managed_file.original_filename or "file",
    )

    if settings.DEBUG:
        try:
            file_handle = managed_file.file.open("rb")
        except (FileNotFoundError, ValueError):
            raise Http404(_("file content not found."))

        response = FileResponse(file_handle, content_type=content_type)
        if disposition:
            response["Content-Disposition"] = disposition
        return response

    response = HttpResponse()
    storage_path = managed_file.file.name.lstrip("/")
    response["X-Accel-Redirect"] = f"{PROTECTED_STORAGE_URL.rstrip('/')}/{storage_path}"
    response["Content-Type"] = content_type
    if disposition:
        response["Content-Disposition"] = disposition
    return response
