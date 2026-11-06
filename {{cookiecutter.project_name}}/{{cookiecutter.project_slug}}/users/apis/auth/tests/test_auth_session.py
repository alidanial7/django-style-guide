import pytest
from {{cookiecutter.project_slug}}.users.tests.api_urls import api_reverse
from rest_framework import status

{%- if cookiecutter.user_login_field == "username" %}


def _login_payload(user, *, password: str = "Password1!x") -> dict:
    return {"username": user.username, "password": password}

{%- else %}


def _login_payload(user, *, password: str = "Password1!x") -> dict:
    return {"email": user.email, "password": password}

{%- endif %}


@pytest.mark.django_db
class TestAuthSession:
    def test_session_login_success(self, api_client, user):
        url = api_reverse("auth:login")
        response = api_client.post(
            url,
            data=_login_payload(user),
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
{%- if cookiecutter.user_login_field == "username" %}
        assert response.data["result"]["username"] == user.username
{%- endif %}
        assert response.data["result"]["email"] == user.email

    def test_session_login_invalid_credentials(self, api_client, user):
        url = api_reverse("auth:login")
        response = api_client.post(
            url,
            data=_login_payload(user, password="wrong-password"),
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_session_logout(self, api_client, user):
        api_client.force_login(user)
        response = api_client.post(api_reverse("auth:logout"), format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

    def test_session_logout_unauthenticated(self, api_client):
        response = api_client.post(api_reverse("auth:logout"), format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN
