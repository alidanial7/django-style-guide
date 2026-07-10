import pytest

from {{cookiecutter.project_slug}}.users.models import Profile
from {{cookiecutter.project_slug}}.users.services.user_services import profile_update, register
from {{cookiecutter.project_slug}}.users.tests.user_factories import BaseUserFactory


@pytest.mark.django_db
class TestUserServices:
    def test_register_creates_user_and_profile(self):
        user = register(email="svc@example.com", password="Password1!x", bio="from service")

        assert user.email == "svc@example.com"
        assert Profile.objects.filter(user=user, bio="from service").exists()

    def test_profile_update(self):
        user = BaseUserFactory()
        profile = user.profile

        updated = profile_update(profile=profile, bio="new bio")

        assert updated.bio == "new bio"
        profile.refresh_from_db()
        assert profile.bio == "new bio"
