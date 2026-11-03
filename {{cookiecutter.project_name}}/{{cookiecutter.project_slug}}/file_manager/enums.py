"""App-level Django choice enums for file_manager.

Define ``models.TextChoices`` / ``IntegerChoices`` here; import them from models,
serializers, filters, and services. Do not nest choice enums inside model classes.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class FileCategory(models.TextChoices):
    """Category of a file for filtering and organization."""

    AVATAR = "avatar", _("avatar")
    IMAGE = "image", _("image")
    DOCUMENT = "document", _("document")
    OTHER = "other", _("other")
