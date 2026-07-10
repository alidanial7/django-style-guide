from django.db.models.signals import post_save
from django.dispatch import receiver

from {{cookiecutter.project_slug}}.users.models import BaseUser, Profile


@receiver(post_save, sender=BaseUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
