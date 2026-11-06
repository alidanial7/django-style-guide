import pytest
from django.urls import reverse
from rest_framework import status

from config.deploy_version import VERSION_FILE_NAME, read_deploy_version


@pytest.mark.django_db
class TestVersionsApi:
    def test_missing_file_returns_null(self, api_client, tmp_path):
        from config import deploy_version as mod

        original = mod.BASE_DIR
        mod.BASE_DIR = tmp_path
        try:
            response = api_client.get(reverse("api:core:versions"))
            assert response.status_code == status.HTTP_200_OK
            assert response.data["success"] is True
            assert response.data["result"]["version"] is None
        finally:
            mod.BASE_DIR = original

    def test_reads_version_file(self, api_client, tmp_path):
        from config import deploy_version as mod

        (tmp_path / VERSION_FILE_NAME).write_text("1.2.3-rc1\n", encoding="utf-8")
        original = mod.BASE_DIR
        mod.BASE_DIR = tmp_path
        try:
            assert read_deploy_version() == "1.2.3-rc1"
            response = api_client.get(reverse("api:core:versions"))
            assert response.status_code == status.HTTP_200_OK
            assert response.data["result"]["version"] == "1.2.3-rc1"
        finally:
            mod.BASE_DIR = original


def test_read_deploy_version_empty_file(tmp_path):
    from config import deploy_version as mod

    (tmp_path / VERSION_FILE_NAME).write_text("   \n", encoding="utf-8")
    original = mod.BASE_DIR
    mod.BASE_DIR = tmp_path
    try:
        assert read_deploy_version() is None
    finally:
        mod.BASE_DIR = original
