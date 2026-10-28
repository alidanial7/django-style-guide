{%- if cookiecutter.use_uuid_pk == "y" %}
import uuid

{%- endif %}
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """
{%- if cookiecutter.use_uuid_pk == "y" %}
    Model to declare shared UUID primary key and timestamp fields
{%- else %}
    Model to declare shared timestamp fields
{%- endif %}
    """

{%- if cookiecutter.use_uuid_pk == "y" %}
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("id"),
        help_text="Random UUID v4 primary key. Not sequential and not guessable.",
    )
{%- endif %}
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
