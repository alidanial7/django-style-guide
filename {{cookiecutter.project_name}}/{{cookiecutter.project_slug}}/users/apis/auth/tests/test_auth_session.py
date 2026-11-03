import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestAuthSession:
    def test_session_login_success(self, api_client, user):
        url = reverse("api:auth:login")
        response = api_client.post(
            url,
            data={"email": user.email, "password": "Password1!x"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["result"]["email"] == user.email

    def test_session_login_invalid_credentials(self, api_client, user):
        url = reverse("api:auth:login")
        response = api_client.post(
            url,
            data={"email": user.email, "password": "wrong-password"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_session_logout(self, api_client, user):
        api_client.force_login(user)
        response = api_client.post(reverse("api:auth:logout"), format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

    def test_session_logout_unauthenticated(self, api_client):
        response = api_client.post(reverse("api:auth:logout"), format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN
