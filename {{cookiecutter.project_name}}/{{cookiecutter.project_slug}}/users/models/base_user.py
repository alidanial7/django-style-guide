from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from {{cookiecutter.project_slug}}.common.models import BaseModel
from {{cookiecutter.project_slug}}.users.manager.user_manager import BaseUserManager


class BaseUser(BaseModel, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="email address", unique=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = BaseUserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_admin
