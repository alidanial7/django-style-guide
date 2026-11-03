import os
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from {{cookiecutter.project_slug}}.common.models import BaseModel
from {{cookiecutter.project_slug}}.file_manager.enums import FileCategory


def generate_secure_file_path(instance: "ManagedFile", filename: str) -> str:
    """Generate storage path partitioned by owning user."""
    ext = os.path.splitext(filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return f"users/{instance.owner_id}/{unique_name}"


class ManagedFile(BaseModel):
    """
    Model to declare managed file
    """

    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
        help_text="Human-readable title or label for the file.",
    )
    original_filename = models.CharField(
        max_length=255,
        verbose_name=_("original filename"),
        help_text="Original filename as uploaded by the client.",
    )
    file = models.FileField(
        upload_to=generate_secure_file_path,
        verbose_name=_("file"),
        help_text="Physical file stored on disk or object storage.",
    )
    file_size = models.PositiveIntegerField(
        verbose_name=_("file size"),
        help_text="File size in bytes.",
    )
    mime_type = models.CharField(
        max_length=100,
        verbose_name=_("mime type"),
        help_text="MIME content type of the file.",
    )
    category = models.CharField(
        max_length=30,
        choices=FileCategory.choices,
        default=FileCategory.OTHER,
        verbose_name=_("category"),
        help_text="Category used for filtering and organizing files.",
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name=_("is public"),
        help_text="Designates whether the file can be downloaded without authentication.",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="managed_files",
        verbose_name=_("owner"),
        help_text="User who uploaded and owns this file.",
    )

    class Meta:
        verbose_name = _("managed file")
        verbose_name_plural = _("managed files")
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["owner", "category"], name="file_mgr_owner_cat_idx"),
            models.Index(fields=["is_public", "category"], name="file_mgr_pub_cat_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.get_category_display()})"

    @property
    def url(self) -> str:
        """Convenience property returning the download URL path."""
        try:
            from django.urls import reverse

            return reverse("api:file_manager:files-download", kwargs={"file_id": self.id})
        except Exception:
            return f"/api/v1/files/{self.id}/download/"
