from __future__ import annotations

from django.contrib.auth import login
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
{%- if cookiecutter.use_jwt == "y" %}
from rest_framework_simplejwt.tokens import RefreshToken
{%- endif %}

from {{cookiecutter.project_slug}}.common.http import api_response
from {{cookiecutter.project_slug}}.common.http.schema import envelope_serializer
from {{cookiecutter.project_slug}}.users.constants import AUTH_TAGS
from {{cookiecutter.project_slug}}.users.services.otp_services import (
    KIND_LOGIN,
    KIND_PROFILE_UPDATE,
    KIND_REGISTER,
    request_otp,
    verify_otp,
)


class AuthOtpRequestInputSerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=20,
        help_text="Mobile number; stored as 98XXXXXXXXXX (e.g. 989134543456).",
    )


class AuthOtpChallengeOutputSerializer(serializers.Serializer):
    phone = serializers.CharField()
    expires_in = serializers.IntegerField()
    resend_in = serializers.IntegerField()
    test_mode = serializers.BooleanField()
    kind = serializers.ChoiceField(
        choices=[KIND_LOGIN, KIND_REGISTER, KIND_PROFILE_UPDATE],
    )


class AuthOtpVerifyInputSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=16)
    kind = serializers.ChoiceField(
        choices=[KIND_LOGIN, KIND_REGISTER, KIND_PROFILE_UPDATE],
        default=KIND_LOGIN,
        help_text=(
            "Must match the challenge kind from request/register/profile. "
            "profile_update requires an authenticated session/JWT."
        ),
    )


{%- if cookiecutter.use_jwt == "y" %}
class AuthOtpVerifyOutputSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    phone = serializers.CharField(allow_null=True)
    kind = serializers.CharField()
{%- else %}
class AuthOtpVerifyOutputSerializer(serializers.Serializer):
    phone = serializers.CharField(allow_null=True)
    detail = serializers.CharField()
    kind = serializers.CharField()
{%- endif %}


class AuthOtpRequestApi(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    @extend_schema(
        tags=AUTH_TAGS,
        summary="Request OTP (SMS) for phone login",
        request=AuthOtpRequestInputSerializer,
        responses=envelope_serializer("AuthOtpRequestEnvelope", AuthOtpChallengeOutputSerializer),
    )
    def post(self, request, *args, **kwargs):
        serializer = AuthOtpRequestInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = request_otp(
            phone=serializer.validated_data["phone"],
            kind=KIND_LOGIN,
        )
        return api_response(data=AuthOtpChallengeOutputSerializer(result).data)


class AuthOtpVerifyApi(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    @extend_schema(
        tags=AUTH_TAGS,
        summary="Verify OTP (login / finish register / confirm phone change)",
        request=AuthOtpVerifyInputSerializer,
        responses=envelope_serializer("AuthOtpVerifyEnvelope", AuthOtpVerifyOutputSerializer),
    )
    def post(self, request, *args, **kwargs):
        serializer = AuthOtpVerifyInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        kind = serializer.validated_data["kind"]
        acting_user = request.user if getattr(request.user, "is_authenticated", False) else None
        user = verify_otp(
            phone=serializer.validated_data["phone"],
            code=serializer.validated_data["code"],
            kind=kind,
            acting_user=acting_user,
        )
{%- if cookiecutter.use_scoped_apis == "y" %}
        from {{cookiecutter.project_slug}}.users.services.scope_membership import (
            ensure_scope_membership_for_request,
        )

        ensure_scope_membership_for_request(request=request, user=user)
{%- endif %}
{%- if cookiecutter.use_jwt == "y" %}
        refresh = RefreshToken.for_user(user)
        payload = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "phone": user.phone,
            "kind": kind,
        }
{%- else %}
        login(request, user)
        payload = {"phone": user.phone, "detail": "logged in", "kind": kind}
{%- endif %}
        return api_response(data=AuthOtpVerifyOutputSerializer(payload).data)
