from unittest.mock import patch

import pytest
from {{cookiecutter.project_slug}}.users.tests.api_urls import api_reverse
from rest_framework import status

from {{cookiecutter.project_slug}}.users.models import BaseUser, SocialAccount
from {{cookiecutter.project_slug}}.users.providers.social.base import SocialIdentity


{%- if cookiecutter.use_google_login == "y" %}
@pytest.mark.django_db
class TestAuthGoogleSocial:
    def test_google_login_creates_user_and_link(self, api_client):
        identity = SocialIdentity(
            provider="google",
            subject="google-sub-1",
            email="google.user@example.com",
            email_verified=True,
        )
        with patch(
            "{{cookiecutter.project_slug}}.users.services.social_auth_services.get_social_provider"
        ) as get_provider:
            get_provider.return_value.verify_id_token.return_value = identity
            response = api_client.post(
                api_reverse("auth:social-google"),
                data={"id_token": "fake.google.token"},
                format="json",
            )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert BaseUser.objects.filter(email="google.user@example.com").exists()
        assert SocialAccount.objects.filter(provider="google", subject="google-sub-1").exists()
{%- if cookiecutter.use_jwt == "y" %}
        assert "access" in response.data["result"]
        assert "refresh" in response.data["result"]
{%- else %}
        assert response.data["result"]["detail"] == "logged in"
{%- endif %}
{%- endif %}


{%- if cookiecutter.use_microsoft_login == "y" %}
@pytest.mark.django_db
class TestAuthMicrosoftSocial:
    def test_microsoft_login_links_existing_email(self, api_client, user):
        identity = SocialIdentity(
            provider="microsoft",
            subject="ms-sub-1",
            email=user.email,
            email_verified=True,
        )
        with patch(
            "{{cookiecutter.project_slug}}.users.services.social_auth_services.get_social_provider"
        ) as get_provider:
            get_provider.return_value.verify_id_token.return_value = identity
            response = api_client.post(
                api_reverse("auth:social-microsoft"),
                data={"id_token": "fake.ms.token"},
                format="json",
            )

        assert response.status_code == status.HTTP_200_OK
        assert SocialAccount.objects.filter(
            provider="microsoft", subject="ms-sub-1", user=user
        ).exists()
{%- endif %}


{%- if cookiecutter.use_apple_login == "y" %}
@pytest.mark.django_db
class TestAuthAppleSocial:
    def test_apple_login_requires_email_on_first_seen(self, api_client):
        identity = SocialIdentity(
            provider="apple",
            subject="apple-sub-1",
            email="",
            email_verified=True,
        )
        with patch(
            "{{cookiecutter.project_slug}}.users.services.social_auth_services.get_social_provider"
        ) as get_provider:
            get_provider.return_value.verify_id_token.return_value = identity
            response = api_client.post(
                api_reverse("auth:social-apple"),
                data={"id_token": "fake.apple.token"},
                format="json",
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
{%- endif %}
