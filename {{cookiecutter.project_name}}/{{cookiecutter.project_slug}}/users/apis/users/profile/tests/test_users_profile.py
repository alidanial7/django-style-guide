import pytest
from django.test import override_settings
from {{cookiecutter.project_slug}}.users.tests.api_urls import api_reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestUsersProfileApi:
    def test_profile_requires_auth(self, api_client):
        url = api_reverse("users:profile")
        response = api_client.get(url)
{%- if cookiecutter.use_jwt == "y" %}
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
{%- else %}
        assert response.status_code == status.HTTP_403_FORBIDDEN
{%- endif %}

    def test_get_profile(self, auth_client, user):
        url = api_reverse("users:profile")
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["result"]["email"] == user.email
{%- if cookiecutter.use_otp_login == "y" %}
        assert response.data["result"]["phone"] == user.phone
{%- endif %}
        assert "bio" in response.data["result"]
        assert response.data["result"]["avatar"]

    def test_patch_profile_bio(self, auth_client):
        url = api_reverse("users:profile")
        response = auth_client.patch(url, data={"bio": "updated bio"}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["result"]["bio"] == "updated bio"
{%- if cookiecutter.use_otp_login == "y" %}

    @override_settings(OTP_TEST=True, OTP_TEST_CODE="12345", OTP_RESEND_SECONDS=0)
    def test_patch_phone_requires_authenticated_otp(self, auth_client, user):
        url = api_reverse("users:profile")
        verify_url = api_reverse("auth:otp-verify")

        pending = auth_client.patch(url, data={"phone": "09131112233"}, format="json")
        assert pending.status_code == status.HTTP_202_ACCEPTED
        assert pending.data["result"]["otp"]["kind"] == "profile_update"
        user.refresh_from_db()
        assert user.phone != "989131112233"

        denied = APIClient().post(
            verify_url,
            data={"phone": "989131112233", "code": "12345", "kind": "profile_update"},
            format="json",
        )
        assert denied.status_code == status.HTTP_400_BAD_REQUEST
        user.refresh_from_db()
        assert user.phone != "989131112233"

        verified = auth_client.post(
            verify_url,
            data={"phone": "989131112233", "code": "12345", "kind": "profile_update"},
            format="json",
        )
        assert verified.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.phone == "989131112233"
{%- endif %}
