from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """
    Model to declare shared timestamp fields
    """

    created_at = models.DateTimeField(
        db_index=True,
        default=timezone.now,
        verbose_name=_("created at"),
        help_text="When this row was first created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("updated at"),
        help_text="When this row was last updated.",
    )

    class Meta:
        abstract = True
