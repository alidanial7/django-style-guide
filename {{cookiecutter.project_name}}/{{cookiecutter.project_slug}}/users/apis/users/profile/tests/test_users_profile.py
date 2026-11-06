import pytest
from django.test import override_settings
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestUsersProfileApi:
    def test_profile_requires_auth(self, api_client):
        url = reverse("api:users:profile")
        response = api_client.get(url)
{%- if cookiecutter.use_jwt == "y" %}
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
{%- else %}
        # SessionAuthentication returns 403 when unauthenticated.
        assert response.status_code == status.HTTP_403_FORBIDDEN
{%- endif %}

    def test_get_profile(self, auth_client, user):
        url = reverse("api:users:profile")
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["result"]["email"] == user.email
{%- if cookiecutter.use_otp_login == "y" %}
        assert "phone" in response.data["result"]
        assert response.data["result"]["phone"] == user.phone
{%- endif %}
        assert "bio" in response.data["result"]
        assert "avatar" in response.data["result"]
        assert response.data["result"]["avatar"]

{%- if cookiecutter.use_otp_login == "y" %}
    @override_settings(OTP_TEST=True, OTP_TEST_CODE="12345")
    def test_patch_profile_requires_otp(self, auth_client, user):
        url = reverse("api:users:profile")
        verify_url = reverse("api:auth:otp-verify")

        pending = auth_client.patch(url, data={"bio": "updated bio"}, format="json")
        assert pending.status_code == status.HTTP_202_ACCEPTED
        assert pending.data["result"]["detail"] == "otp_required"
        assert pending.data["result"]["otp"]["phone"] == user.phone
        user.profile.refresh_from_db()
        assert user.profile.bio != "updated bio"

        verified = auth_client.post(
            verify_url,
            data={"phone": user.phone, "code": "12345"},
            format="json",
        )
        assert verified.status_code == status.HTTP_200_OK
        user.profile.refresh_from_db()
        assert user.profile.bio == "updated bio"

    @override_settings(OTP_TEST=True, OTP_TEST_CODE="12345")
    def test_patch_profile_phone_change_requires_otp(self, auth_client, user):
        url = reverse("api:users:profile")
        verify_url = reverse("api:auth:otp-verify")

        pending = auth_client.patch(url, data={"phone": "09131112233"}, format="json")
        assert pending.status_code == status.HTTP_202_ACCEPTED
        assert pending.data["result"]["otp"]["phone"] == "989131112233"
        user.refresh_from_db()
        assert user.phone != "989131112233"

        verified = auth_client.post(
            verify_url,
            data={"phone": "989131112233", "code": "12345"},
            format="json",
        )
        assert verified.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.phone == "989131112233"
{%- else %}
    def test_patch_profile_bio(self, auth_client):
        url = reverse("api:users:profile")
        response = auth_client.patch(url, data={"bio": "updated bio"}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["result"]["bio"] == "updated bio"
{%- endif %}
