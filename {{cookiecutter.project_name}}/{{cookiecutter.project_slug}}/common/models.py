from django.db import models
from django.db.models.query import F, Q
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


class RandomModel(BaseModel):
    """
    Model to declare random date range example
    """

    start_date = models.DateField(
        verbose_name=_("start date"),
        help_text="Inclusive start of the range.",
    )
    end_date = models.DateField(
        verbose_name=_("end date"),
        help_text="Exclusive-style end bound used by the check constraint.",
    )

    class Meta:
        verbose_name = _("random model")
        verbose_name_plural = _("random models")
        constraints = [
            models.CheckConstraint(
                name="start_date_before_end_date",
                condition=Q(start_date__lt=F("end_date")),
            )
        ]
