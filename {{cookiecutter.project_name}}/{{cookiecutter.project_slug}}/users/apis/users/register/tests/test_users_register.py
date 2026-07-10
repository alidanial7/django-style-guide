import pytest
from django.core.exceptions import ValidationError as DjangoValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from {{cookiecutter.project_slug}}.common.errors.codes import ErrorCode
from {{cookiecutter.project_slug}}.common.http.exception_handler import api_exception_handler
from {{cookiecutter.project_slug}}.core.exceptions import ApplicationError
from {{cookiecutter.project_slug}}.users.apis.users.register.users_register_serializers import (
    UsersRegisterInputSerializer,
)
from {{cookiecutter.project_slug}}.users.errors.codes import UserErrorCode


@pytest.mark.django_db
class TestUsersRegisterValidation:
    def test_register_success(self, api_client):
        url = reverse("api:users:register")
        payload = {
            "email": "new@example.com",
            "password": "Password1!x",
            "confirm_password": "Password1!x",
            "bio": "hello",
        }

        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["email"] == "new@example.com"
        assert "access" in response.data["token"]

    def test_register_password_mismatch(self, api_client):
        url = reverse("api:users:register")
        payload = {
            "email": "new@example.com",
            "password": "Password1!x",
            "confirm_password": "Password2!x",
        }

        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
        assert response.data["result"] == []
        item = response.data["messages"]["confirm_password"][0]
        assert item["code"] == UserErrorCode.PASSWORD_MISMATCH
        assert "confirm password" in item["message"]

    def test_register_duplicate_email(self, api_client, user):
        url = reverse("api:users:register")
        payload = {
            "email": user.email,
            "password": "Password1!x",
            "confirm_password": "Password1!x",
        }

        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
        item = response.data["messages"]["email"][0]
        assert item["code"] == ErrorCode.UNIQUE
        assert "message" in item


def test_register_serializer_object_rule():
    serializer = UsersRegisterInputSerializer(
        data={
            "email": "a@example.com",
            "password": "Password1!x",
            "confirm_password": "other",
        }
    )
    assert serializer.is_valid() is False
    assert "confirm_password" in serializer.errors


def test_exception_handler_envelope_shape():
    factory = APIRequestFactory()
    request = factory.get("/")

    response = api_exception_handler(
        ValidationError({"email": [ErrorDetail("email already exists.", code="unique")]}),
        {"request": request, "view": APIView()},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        "success": False,
        "status": 400,
        "result": [],
        "messages": {
            "email": [{"message": "email already exists.", "code": "unique"}],
        },
    }


def test_exception_handler_django_validation_error():
    factory = APIRequestFactory()
    request = factory.get("/")

    response = api_exception_handler(
        DjangoValidationError({"email": ["already exists."]}),
        {"request": request, "view": APIView()},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False
    assert response.data["status"] == 400
    assert response.data["result"] == []
    item = response.data["messages"]["email"][0]
    assert "message" in item
    assert "code" in item


def test_exception_handler_application_error():
    factory = APIRequestFactory()
    request = factory.get("/")

    response = api_exception_handler(
        ApplicationError("something went wrong", extra={"order_id": "missing"}),
        {"request": request, "view": APIView()},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False
    assert response.data["status"] == 400
    assert response.data["result"] == []
    assert response.data["messages"]["non_field_errors"] == [
        {"message": "something went wrong", "code": ErrorCode.APPLICATION_ERROR},
    ]
    assert response.data["messages"]["order_id"] == [
        {"message": "missing", "code": ErrorCode.INVALID},
    ]


def test_exception_handler_unexpected_server_error():
    factory = APIRequestFactory()
    request = factory.get("/")

    response = api_exception_handler(
        RuntimeError("secret internals"),
        {"request": request, "view": APIView()},
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {
        "success": False,
        "status": 500,
        "result": [],
        "messages": {
            "non_field_errors": [
                {"message": "a server error occurred.", "code": ErrorCode.SERVER_ERROR},
            ]
        },
    }
    assert "secret" not in str(response.data)
