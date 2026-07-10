import pytest
from rest_framework.test import APIClient

from {{cookiecutter.project_slug}}.users.tests.user_factories import BaseUserFactory


@pytest.fixture
def user(db):
    return BaseUserFactory()


@pytest.fixture
def auth_client(user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client
