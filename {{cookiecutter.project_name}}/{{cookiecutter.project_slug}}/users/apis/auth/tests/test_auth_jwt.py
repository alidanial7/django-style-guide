import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
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
