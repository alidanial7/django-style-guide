from django.db import transaction

from .models import BaseUser, Profile


def create_user(*, email: str, password: str) -> BaseUser:
    return BaseUser.objects.create_user(email=email, password=password)


@transaction.atomic
def register(*, bio: str | None, email: str, password: str) -> BaseUser:
    user = create_user(email=email, password=password)

    if bio:
        profile = Profile.objects.get(user=user)
        profile.bio = bio
        profile.save(update_fields=["bio"])

    return user
