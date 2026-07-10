import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from {{cookiecutter.project_slug}}.users.tests.user_factories import BaseUserFactory


@pytest.fixture
def user(db):
    return BaseUserFactory()


@pytest.fixture
def auth_client(user) -> APIClient:
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client
