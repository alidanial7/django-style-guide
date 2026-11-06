import pytest
from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import override_settings
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
{%- if cookiecutter.use_otp_login == "y" %}
from {{cookiecutter.project_slug}}.users.models import BaseUser
{%- endif %}


@pytest.mark.django_db
class TestUsersRegisterValidation:
{%- if cookiecutter.use_otp_login == "y" %}
    @override_settings(OTP_TEST=True, OTP_TEST_CODE="12345")
    def test_register_pending_then_otp_creates_user(self, api_client):
        register_url = reverse("api:users:register")
        verify_url = reverse("api:auth:otp-verify")
        payload = {
{%- if cookiecutter.user_login_field == "username" %}
            "username": "newuser",
{%- endif %}
            "email": "new@example.com",
            "phone": "09134543456",
            "password": "Password1!x",
            "confirm_password": "Password1!x",
            "bio": "hello",
        }

        pending = api_client.post(register_url, data=payload, format="json")
        assert pending.status_code == status.HTTP_202_ACCEPTED
        assert pending.data["result"]["detail"] == "otp_required"
        assert pending.data["result"]["otp"]["phone"] == "989134543456"
        assert not BaseUser.objects.filter(email="new@example.com").exists()

        verified = api_client.post(
            verify_url,
            data={"phone": "989134543456", "code": "12345"},
            format="json",
        )
        assert verified.status_code == status.HTTP_200_OK
        user = BaseUser.objects.get(email="new@example.com")
        assert user.phone == "989134543456"
        assert user.profile.bio == "hello"
{%- if cookiecutter.use_jwt == "y" %}
        assert "access" in verified.data["result"]
{%- endif %}
{%- else %}
    def test_register_success(self, api_client):
        url = reverse("api:users:register")
        payload = {
{%- if cookiecutter.user_login_field == "username" %}
            "username": "newuser",
{%- endif %}
            "email": "new@example.com",
            "password": "Password1!x",
            "confirm_password": "Password1!x",
            "bio": "hello",
        }

        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert response.data["status"] == 201
{%- if cookiecutter.user_login_field == "username" %}
        assert response.data["result"]["username"] == "newuser"
{%- endif %}
        assert response.data["result"]["email"] == "new@example.com"
{%- if cookiecutter.use_jwt == "y" %}
        assert "access" in response.data["result"]["token"]
{%- endif %}
{%- endif %}

    def test_register_password_mismatch(self, api_client):
        url = reverse("api:users:register")
        payload = {
{%- if cookiecutter.user_login_field == "username" %}
            "username": "newuser",
{%- endif %}
            "email": "new@example.com",
{%- if cookiecutter.use_otp_login == "y" %}
            "phone": "09134543456",
{%- endif %}
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

{%- if cookiecutter.use_otp_login != "y" %}
    def test_register_duplicate_email(self, api_client, user):
        url = reverse("api:users:register")
        payload = {
{%- if cookiecutter.user_login_field == "username" %}
            "username": "anotheruser",
{%- endif %}
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
{%- endif %}


def test_register_serializer_object_rule():
    serializer = UsersRegisterInputSerializer(
        data={
{%- if cookiecutter.user_login_field == "username" %}
            "username": "a_user",
{%- endif %}
            "email": "a@example.com",
{%- if cookiecutter.use_otp_login == "y" %}
            "phone": "09134543456",
{%- endif %}
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
