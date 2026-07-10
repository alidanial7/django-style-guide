import pytest
from django.urls import reverse
from rest_framework import status

from {{cookiecutter.project_slug}}.users.models import BaseUser, Profile


@pytest.mark.django_db
class TestUsersRegisterApi:
    def test_register_success(self, api_client):
        url = reverse("api:users:register")
        payload = {
            "email": "new@example.com",
            "password": "Password1!x",
            "confirm_password": "Password1!x",
            "bio": "hello",
        }

        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "new@example.com"
        assert "access" in response.data["token"]
        assert "refresh" in response.data["token"]
        assert BaseUser.objects.filter(email="new@example.com").exists()
        assert Profile.objects.filter(user__email="new@example.com", bio="hello").exists()

    def test_register_password_mismatch(self, api_client):
        url = reverse("api:users:register")
        payload = {
            "email": "new@example.com",
            "password": "Password1!x",
            "confirm_password": "Password2!x",
        }

        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_email(self, api_client, user):
        url = reverse("api:users:register")
        payload = {
            "email": user.email,
            "password": "Password1!x",
            "confirm_password": "Password1!x",
        }

        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
