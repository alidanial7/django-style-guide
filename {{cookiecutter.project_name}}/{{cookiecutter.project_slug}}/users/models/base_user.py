from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from {{cookiecutter.project_slug}}.common.models import BaseModel
from {{cookiecutter.project_slug}}.users.manager.user_manager import BaseUserManager


class BaseUser(BaseModel, AbstractBaseUser, PermissionsMixin):
    """
    Model to declare user
    """

    email = models.EmailField(
        unique=True,
        verbose_name=_("email"),
        help_text="Primary login identifier for the account.",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is active"),
        help_text="Designates whether this user can authenticate.",
    )
    is_admin = models.BooleanField(
        default=False,
        verbose_name=_("is admin"),
        help_text="Designates whether this user has admin/staff access.",
    )

    objects = BaseUserManager()

    USERNAME_FIELD = "email"

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_admin
