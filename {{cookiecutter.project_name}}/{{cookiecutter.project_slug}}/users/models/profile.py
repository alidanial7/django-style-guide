from django.db import models
from django.utils.translation import gettext_lazy as _

from {{cookiecutter.project_slug}}.users.models.base_user import BaseUser


class Profile(models.Model):
    """
    Model to declare profile
    """

    user = models.OneToOneField(
        BaseUser,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("user"),
        help_text="Account this profile belongs to.",
    )
    bio = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
        verbose_name=_("bio"),
        help_text="Optional short biography shown on the profile.",
    )
    avatar = models.ImageField(
        upload_to="profiles/avatars/",
        blank=True,
        null=True,
        verbose_name=_("avatar"),
        help_text="Optional profile image.",
    )

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")

    def __str__(self):
        return f"{self.user.email}"
