import pytest
from django.test import RequestFactory

from {{cookiecutter.project_slug}}.users.selectors.users_selectors import get_avatar_url, get_profile
from {{cookiecutter.project_slug}}.users.tests.user_factories import BaseUserFactory


@pytest.mark.django_db
class TestUsersSelectors:
    def test_get_profile_creates_missing_profile(self):
        user = BaseUserFactory()
        user.profile.delete()

        profile = get_profile(user=user)

        assert profile.user_id == user.id

    def test_get_avatar_url_default(self):
        user = BaseUserFactory()
        request = RequestFactory().get("/")

        url = get_avatar_url(profile=user.profile, request=request)

        assert url.endswith("/static/users/default_avatar.png")
