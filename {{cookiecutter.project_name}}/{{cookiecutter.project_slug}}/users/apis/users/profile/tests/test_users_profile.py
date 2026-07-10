import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestUsersProfileApi:
    def test_profile_requires_auth(self, api_client):
        url = reverse("api:users:profile")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_profile(self, auth_client, user):
        url = reverse("api:users:profile")
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email
        assert "bio" in response.data
        assert "avatar" in response.data
        assert response.data["avatar"]

    def test_patch_profile_bio(self, auth_client):
        url = reverse("api:users:profile")
        response = auth_client.patch(url, data={"bio": "updated bio"}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["bio"] == "updated bio"
