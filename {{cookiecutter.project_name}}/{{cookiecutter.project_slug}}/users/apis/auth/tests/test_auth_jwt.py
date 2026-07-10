import pytest
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status

from {{cookiecutter.project_slug}}.users.errors.codes import UserErrorCode


@pytest.mark.django_db
{%- if cookiecutter.use_jwt == "y" %}
class TestAuthJwt:
    def test_login_success(self, api_client, user):
        url = reverse("api:auth:login")
        response = api_client.post(
            url,
            data={"email": user.email, "password": "Password1!x"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert "access" in response.data["result"]
        assert "refresh" in response.data["result"]

    def test_login_invalid_credentials(self, api_client, user):
        url = reverse("api:auth:login")
        response = api_client.post(
            url,
            data={"email": user.email, "password": "wrong-password"},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_refresh_rotates_token(self, api_client, user):
        login_url = reverse("api:auth:login")
        refresh_url = reverse("api:auth:refresh")

        login = api_client.post(
            login_url,
            data={"email": user.email, "password": "Password1!x"},
            format="json",
        )
        assert login.status_code == status.HTTP_200_OK
        old_refresh = login.data["result"]["refresh"]

        refreshed = api_client.post(refresh_url, data={"refresh": old_refresh}, format="json")
        assert refreshed.status_code == status.HTTP_200_OK
        assert "access" in refreshed.data["result"]
        assert "refresh" in refreshed.data["result"]
        assert refreshed.data["result"]["refresh"] != old_refresh

        reuse = api_client.post(refresh_url, data={"refresh": old_refresh}, format="json")
        assert reuse.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_blacklists_refresh(self, api_client, user):
        login = api_client.post(
            reverse("api:auth:login"),
            data={"email": user.email, "password": "Password1!x"},
            format="json",
        )
        refresh = login.data["result"]["refresh"]

        logout = api_client.post(
            reverse("api:auth:logout"),
            data={"refresh": refresh},
            format="json",
        )
        assert logout.status_code == status.HTTP_200_OK
        assert logout.data["success"] is True

        reuse = api_client.post(
            reverse("api:auth:refresh"),
            data={"refresh": refresh},
            format="json",
        )
        assert reuse.status_code == status.HTTP_401_UNAUTHORIZED
{%- else %}
class TestAuthSession:
    def test_login_success(self, api_client, user):
        url = reverse("api:auth:login")
        response = api_client.post(
            url,
            data={"email": user.email, "password": "Password1!x"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["result"]["email"] == user.email

    def test_login_invalid_credentials(self, api_client, user):
        url = reverse("api:auth:login")
        response = api_client.post(
            url,
            data={"email": user.email, "password": "wrong-password"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_logout(self, api_client, user):
        api_client.force_login(user)
        response = api_client.post(reverse("api:auth:logout"), format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
{%- endif %}


@pytest.mark.django_db
class TestAuthPassword:
    def test_change_password(self, auth_client, api_client, user):
        url = reverse("api:auth:password-change")
        response = auth_client.post(
            url,
            data={
                "current_password": "Password1!x",
                "new_password": "Password2!x",
                "confirm_password": "Password2!x",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

        login = api_client.post(
            reverse("api:auth:login"),
            data={"email": user.email, "password": "Password2!x"},
            format="json",
        )
        assert login.status_code == status.HTTP_200_OK

    def test_change_password_wrong_current(self, auth_client):
        response = auth_client.post(
            reverse("api:auth:password-change"),
            data={
                "current_password": "WrongPass1!",
                "new_password": "Password2!x",
                "confirm_password": "Password2!x",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["messages"]["current_password"][0]["code"] == UserErrorCode.PASSWORD_INCORRECT

    def test_password_reset_flow(self, api_client, user):
        request_resp = api_client.post(
            reverse("api:auth:password-reset"),
            data={"email": user.email},
            format="json",
        )
        assert request_resp.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 1

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)

        confirm = api_client.post(
            reverse("api:auth:password-reset-confirm"),
            data={
                "uid": uid,
                "token": token,
                "new_password": "Password3!x",
                "confirm_password": "Password3!x",
            },
            format="json",
        )
        assert confirm.status_code == status.HTTP_200_OK

        login = api_client.post(
            reverse("api:auth:login"),
            data={"email": user.email, "password": "Password3!x"},
            format="json",
        )
        assert login.status_code == status.HTTP_200_OK

    def test_password_reset_unknown_email_is_silent(self, api_client):
        response = api_client.post(
            reverse("api:auth:password-reset"),
            data={"email": "missing@example.com"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 0
