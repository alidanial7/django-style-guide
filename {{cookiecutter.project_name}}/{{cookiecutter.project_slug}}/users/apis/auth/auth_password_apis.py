from drf_spectacular.utils import extend_schema
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from {{cookiecutter.project_slug}}.api.mixins import ApiAuthMixin
from {{cookiecutter.project_slug}}.common.http import api_response
from {{cookiecutter.project_slug}}.users.apis.auth.auth_serializers import (
    AuthPasswordChangeInputSerializer,
    AuthPasswordResetConfirmInputSerializer,
    AuthPasswordResetRequestInputSerializer,
)
from {{cookiecutter.project_slug}}.users.constants import AUTH_TAGS
from {{cookiecutter.project_slug}}.users.services.user_services import (
    change_password,
    request_password_reset,
    reset_password,
)


class AuthPasswordChangeApi(ApiAuthMixin, APIView):
    @extend_schema(
        tags=AUTH_TAGS,
        summary="Change password (authenticated)",
        request=AuthPasswordChangeInputSerializer,
    )
    def post(self, request):
        serializer = AuthPasswordChangeInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        change_password(
            user=request.user,
            current_password=serializer.validated_data["current_password"],
            new_password=serializer.validated_data["new_password"],
        )
        return api_response(data={"detail": "password changed."})


class AuthPasswordResetRequestApi(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset"

    @extend_schema(
        tags=AUTH_TAGS,
        summary="Request password reset email",
        request=AuthPasswordResetRequestInputSerializer,
    )
    def post(self, request):
        serializer = AuthPasswordResetRequestInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_password_reset(email=serializer.validated_data["email"])
        return api_response(
            data={"detail": "if an account exists for this email, a reset message was sent."}
        )


class AuthPasswordResetConfirmApi(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset"

    @extend_schema(
        tags=AUTH_TAGS,
        summary="Confirm password reset",
        request=AuthPasswordResetConfirmInputSerializer,
    )
    def post(self, request):
        serializer = AuthPasswordResetConfirmInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reset_password(
            uidb64=serializer.validated_data["uid"],
            token=serializer.validated_data["token"],
            new_password=serializer.validated_data["new_password"],
        )
        return api_response(data={"detail": "password reset."})
