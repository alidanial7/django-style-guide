from django.db import transaction

from {{cookiecutter.project_slug}}.users.models import BaseUser, Profile


def create_user(*, email: str, password: str) -> BaseUser:
    return BaseUser.objects.create_user(email=email, password=password)


@transaction.atomic
def register(
    *,
    email: str,
    password: str,
    bio: str | None = None,
    avatar=None,
) -> BaseUser:
    user = create_user(email=email, password=password)
    profile = Profile.objects.get(user=user)

    update_fields: list[str] = []
    if bio:
        profile.bio = bio
        update_fields.append("bio")
    if avatar is not None:
        profile.avatar = avatar
        update_fields.append("avatar")

    if update_fields:
        profile.save(update_fields=update_fields)

    return user


@transaction.atomic
def profile_update(*, profile: Profile, bio: str | None = None, avatar=None) -> Profile:
    update_fields: list[str] = []

    if bio is not None:
        profile.bio = bio
        update_fields.append("bio")
    if avatar is not None:
        profile.avatar = avatar
        update_fields.append("avatar")

    if update_fields:
        profile.save(update_fields=update_fields)

    return profile
