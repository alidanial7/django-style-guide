from django.http import HttpRequest
from django.templatetags.static import static

from .models import BaseUser, Profile

DEFAULT_AVATAR_STATIC_PATH = "users/default_avatar.png"


def get_profile(user: BaseUser) -> Profile:
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def get_avatar_url(*, profile: Profile, request: HttpRequest | None = None) -> str:
    if profile.avatar:
        url = profile.avatar.url
    else:
        url = static(DEFAULT_AVATAR_STATIC_PATH)

    if request is not None:
        return request.build_absolute_uri(url)
    return url
