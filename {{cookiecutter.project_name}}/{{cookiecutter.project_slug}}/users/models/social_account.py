from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from {{cookiecutter.project_slug}}.common.models import BaseModel


class SocialAccount(BaseModel):
    """Links an external OAuth subject to a local user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="social_accounts",
        verbose_name=_("user"),
    )
    provider = models.CharField(max_length=32, verbose_name=_("provider"))
    subject = models.CharField(max_length=255, verbose_name=_("subject"))

    class Meta:
        verbose_name = _("social account")
        verbose_name_plural = _("social accounts")
        constraints = [
            models.UniqueConstraint(
                fields=("provider", "subject"),
                name="users_socialaccount_provider_subject_uniq",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.provider}:{self.subject}"
