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
from {{cookiecutter.project_slug}}.users.services.otp_services import request_otp, verify_otp


class AuthOtpRequestInputSerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=20,
        help_text="Mobile number; stored as 98XXXXXXXXXX (e.g. 989134543456).",
    )


class AuthOtpRequestOutputSerializer(serializers.Serializer):
    phone = serializers.CharField()
    expires_in = serializers.IntegerField()
    resend_in = serializers.IntegerField()
    test_mode = serializers.BooleanField()


class AuthOtpVerifyInputSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=16)


{%- if cookiecutter.use_jwt == "y" %}
class AuthOtpVerifyOutputSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    phone = serializers.CharField()
{%- else %}
class AuthOtpVerifyOutputSerializer(serializers.Serializer):
    phone = serializers.CharField()
    detail = serializers.CharField()
{%- endif %}


class AuthOtpRequestApi(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    @extend_schema(
        tags=AUTH_TAGS,
        summary="Request OTP (SMS)",
        request=AuthOtpRequestInputSerializer,
        responses=envelope_serializer("AuthOtpRequestEnvelope", AuthOtpRequestOutputSerializer),
    )
    def post(self, request, *args, **kwargs):
        serializer = AuthOtpRequestInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = request_otp(phone=serializer.validated_data["phone"])
        return api_response(data=AuthOtpRequestOutputSerializer(result).data)


class AuthOtpVerifyApi(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    @extend_schema(
        tags=AUTH_TAGS,
        summary="Verify OTP and log in",
        request=AuthOtpVerifyInputSerializer,
        responses=envelope_serializer("AuthOtpVerifyEnvelope", AuthOtpVerifyOutputSerializer),
    )
    def post(self, request, *args, **kwargs):
        serializer = AuthOtpVerifyInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = verify_otp(
            phone=serializer.validated_data["phone"],
            code=serializer.validated_data["code"],
        )
{%- if cookiecutter.use_jwt == "y" %}
        refresh = RefreshToken.for_user(user)
        payload = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "phone": user.phone,
        }
{%- else %}
        login(request, user)
        payload = {"phone": user.phone, "detail": "logged in"}
{%- endif %}
        return api_response(data=AuthOtpVerifyOutputSerializer(payload).data)
