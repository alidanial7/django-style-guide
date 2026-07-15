import pytest

from {{cookiecutter.project_slug}}.users.models import Profile
from {{cookiecutter.project_slug}}.users.services.user_services import profile_update, register
from {{cookiecutter.project_slug}}.users.tests.user_factories import BaseUserFactory
from {{cookiecutter.project_slug}}.users.types import ProfileUpdateData, RegisterData


@pytest.mark.django_db
class TestUserServices:
    def test_register_creates_user_and_profile(self):
        data: RegisterData = {
            "email": "svc@example.com",
            "password": "Password1!x",
            "bio": "from service",
        }
        user = register(data=data)

        assert user.email == "svc@example.com"
        assert Profile.objects.filter(user=user, bio="from service").exists()

    def test_profile_update(self):
        user = BaseUserFactory()
        profile = user.profile

        data: ProfileUpdateData = {"bio": "new bio"}
        updated = profile_update(profile=profile, data=data)

        assert updated.bio == "new bio"
        profile.refresh_from_db()
        assert profile.bio == "new bio"

    def test_profile_update_skips_absent_keys(self):
        user = BaseUserFactory()
        profile = user.profile
        profile.bio = "keep me"
        profile.save(update_fields=["bio"])

        updated = profile_update(profile=profile, data={})

        assert updated.bio == "keep me"

    def test_profile_update_none_clears_when_sent(self):
        user = BaseUserFactory()
        profile = user.profile
        profile.bio = "keep me"
        profile.save(update_fields=["bio"])

        data: ProfileUpdateData = {"bio": None}
        updated = profile_update(profile=profile, data=data)

        assert updated.bio is None
