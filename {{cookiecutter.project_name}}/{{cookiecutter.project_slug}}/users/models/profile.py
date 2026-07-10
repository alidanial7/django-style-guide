from django.db import models

from {{cookiecutter.project_slug}}.users.models.base_user import BaseUser


class Profile(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, related_name="profile")
    bio = models.CharField(max_length=1000, null=True, blank=True)
    avatar = models.ImageField(upload_to="profiles/avatars/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.email}"
