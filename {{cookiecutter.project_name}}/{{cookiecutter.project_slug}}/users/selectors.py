from .models import BaseUser, Profile


def get_profile(user: BaseUser) -> Profile:
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile
