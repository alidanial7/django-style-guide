from django.db import IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver

from {{cookiecutter.project_slug}}.users.models import BaseUser, Profile


@receiver(post_save, sender=BaseUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Create Profile for new users. Not an API boundary — absorb create races."""
    if not created:
        return
    try:
        Profile.objects.get_or_create(user=instance)
    except IntegrityError:
        Profile.objects.get(user=instance)
