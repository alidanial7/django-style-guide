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
from {{cookiecutter.project_slug}}.users.services.social_auth_services import social_login


class AuthSocialLoginInputSerializer(serializers.Serializer):
    id_token = serializers.CharField(
        help_text="OIDC ID token from the provider SDK / frontend.",
    )


{%- if cookiecutter.use_jwt == "y" %}
class AuthSocialLoginOutputSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    email = serializers.EmailField()
    provider = serializers.CharField()
{%- else %}
class AuthSocialLoginOutputSerializer(serializers.Serializer):
    email = serializers.EmailField()
    provider = serializers.CharField()
    detail = serializers.CharField()
{%- endif %}


class _AuthSocialLoginBase(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"
    provider_name: str = ""

    def post(self, request, *args, **kwargs):
        serializer = AuthSocialLoginInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = social_login(
            provider=self.provider_name,
            id_token=serializer.validated_data["id_token"],
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
            "email": user.email,
            "provider": self.provider_name,
        }
{%- else %}
        login(request, user)
        payload = {
            "email": user.email,
            "provider": self.provider_name,
            "detail": "logged in",
        }
{%- endif %}
        return api_response(data=AuthSocialLoginOutputSerializer(payload).data)


{%- if cookiecutter.use_google_login == "y" %}
class AuthGoogleLoginApi(_AuthSocialLoginBase):
    provider_name = "google"

    @extend_schema(
        tags=AUTH_TAGS,
        summary="Google social login",
        request=AuthSocialLoginInputSerializer,
        responses=envelope_serializer("AuthGoogleLoginEnvelope", AuthSocialLoginOutputSerializer),
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

{%- endif %}
{%- if cookiecutter.use_microsoft_login == "y" %}
class AuthMicrosoftLoginApi(_AuthSocialLoginBase):
    provider_name = "microsoft"

    @extend_schema(
        tags=AUTH_TAGS,
        summary="Microsoft social login",
        request=AuthSocialLoginInputSerializer,
        responses=envelope_serializer(
            "AuthMicrosoftLoginEnvelope", AuthSocialLoginOutputSerializer
        ),
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

{%- endif %}
{%- if cookiecutter.use_apple_login == "y" %}
class AuthAppleLoginApi(_AuthSocialLoginBase):
    provider_name = "apple"

    @extend_schema(
        tags=AUTH_TAGS,
        summary="Apple social login",
        request=AuthSocialLoginInputSerializer,
        responses=envelope_serializer("AuthAppleLoginEnvelope", AuthSocialLoginOutputSerializer),
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
{%- endif %}
