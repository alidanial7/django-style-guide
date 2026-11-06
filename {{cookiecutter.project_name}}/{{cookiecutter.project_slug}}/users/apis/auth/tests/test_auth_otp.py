import pytest
from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from {{cookiecutter.project_slug}}.users.models import BaseUser


@pytest.mark.django_db
class TestAuthOtp:
    @override_settings(OTP_TEST=True, OTP_TEST_CODE="12345")
    def test_request_and_verify_creates_user(self, api_client):
        request_url = reverse("api:auth:otp-request")
        verify_url = reverse("api:auth:otp-verify")

        requested = api_client.post(
            request_url,
            data={"phone": "09134543456"},
            format="json",
        )
        assert requested.status_code == status.HTTP_200_OK
        assert requested.data["success"] is True
        assert requested.data["result"]["phone"] == "989134543456"
        assert requested.data["result"]["test_mode"] is True

        verified = api_client.post(
            verify_url,
            data={"phone": "989134543456", "code": "12345"},
            format="json",
        )
        assert verified.status_code == status.HTTP_200_OK
        assert verified.data["success"] is True
        assert BaseUser.objects.filter(phone="989134543456").exists()
{%- if cookiecutter.use_jwt == "y" %}
        assert "access" in verified.data["result"]
        assert "refresh" in verified.data["result"]
{%- else %}
        assert verified.data["result"]["detail"] == "logged in"
{%- endif %}

    @override_settings(OTP_TEST=True, OTP_TEST_CODE="12345")
    def test_verify_rejects_wrong_code(self, api_client):
        url = reverse("api:auth:otp-verify")
        response = api_client.post(
            url,
            data={"phone": "989134543456", "code": "00000"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_request_rejects_invalid_phone(self, api_client):
        url = reverse("api:auth:otp-request")
        response = api_client.post(url, data={"phone": "123"}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
