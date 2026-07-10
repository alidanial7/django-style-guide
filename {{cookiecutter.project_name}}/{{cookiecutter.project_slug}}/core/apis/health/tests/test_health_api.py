import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestHealthApi:
    def test_health_reports_django_and_database(self, api_client):
        url = reverse("api:core:health")
        response = api_client.get(url)

        assert response.status_code in (status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE)
        assert "django" in response.data["checks"]
        assert "database" in response.data["checks"]
        assert response.data["checks"]["django"]["status"] == "ok"
        assert response.data["checks"]["database"]["status"] == "ok"
