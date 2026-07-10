import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestHealthApi:
    def test_health_reports_django_and_database(self, api_client):
        url = reverse("api:core:health")
        response = api_client.get(url)

        assert response.status_code in (status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE)
        assert response.data["success"] is True
        payload = response.data["result"]
        assert "django" in payload["checks"]
        assert "database" in payload["checks"]
        assert payload["checks"]["django"]["status"] == "ok"
        assert payload["checks"]["database"]["status"] == "ok"
