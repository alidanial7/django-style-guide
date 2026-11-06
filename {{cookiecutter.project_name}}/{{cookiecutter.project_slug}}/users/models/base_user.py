from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from {{cookiecutter.project_slug}}.common.models import BaseModel
from {{cookiecutter.project_slug}}.users.manager.user_manager import BaseUserManager


class BaseUser(BaseModel, AbstractBaseUser, PermissionsMixin):
    """
    Model to declare user
    """

{%- if cookiecutter.user_login_field == "username" %}
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name=_("username"),
        help_text="Primary login identifier for the account.",
    )
    email = models.EmailField(
        unique=True,
        verbose_name=_("email"),
        help_text="Contact email (password reset and notifications).",
    )
{%- else %}
    email = models.EmailField(
        unique=True,
        verbose_name=_("email"),
        help_text="Primary login identifier for the account.",
    )
{%- endif %}
{%- if cookiecutter.use_otp_login == "y" %}
    phone = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_("phone"),
        help_text="Mobile in E.164 digits without '+', e.g. 989134543456.",
    )
{%- endif %}
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

{%- if cookiecutter.user_login_field == "username" %}
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]
{%- else %}
    USERNAME_FIELD = "email"
{%- endif %}

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
{%- if cookiecutter.user_login_field == "username" %}
        return self.username
{%- else %}
        return self.email
{%- endif %}

    @property
    def is_staff(self):
        return self.is_admin
