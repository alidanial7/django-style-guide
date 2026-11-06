from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from {{cookiecutter.project_slug}}.common.http import api_response
from {{cookiecutter.project_slug}}.common.http.schema import envelope_serializer
from {{cookiecutter.project_slug}}.users.constants import AUTH_TAGS


class AuthJwtTokenObtainSerializer(TokenObtainPairSerializer):
{%- if cookiecutter.user_login_field == "username" %}
    """Obtain pair; field name follows USERNAME_FIELD (username) for schema + clients."""
{%- else %}
    """Obtain pair; field name follows USERNAME_FIELD (email) for schema + clients."""
{%- endif %}


class AuthJwtTokenPairOutputSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class AuthJwtRefreshOutputSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField(required=False)


class AuthJwtLoginApi(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = AuthJwtTokenObtainSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    @extend_schema(
        tags=AUTH_TAGS,
        summary="JWT login",
        request=AuthJwtTokenObtainSerializer,
        responses=envelope_serializer("AuthJwtLoginEnvelope", AuthJwtTokenPairOutputSerializer),
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
{%- if cookiecutter.use_scoped_apis == "y" %}
        if response.status_code < 400:
            from {{cookiecutter.project_slug}}.users.models import BaseUser
            from {{cookiecutter.project_slug}}.users.services.scope_membership import (
                ensure_scope_membership_for_request,
            )

{%- if cookiecutter.user_login_field == "username" %}
            ident = request.data.get("username")
            user = BaseUser.objects.filter(username=ident).first() if ident else None
{%- else %}
            ident = request.data.get("email")
            user = BaseUser.objects.filter(email=ident).first() if ident else None
{%- endif %}
            if user is not None:
                ensure_scope_membership_for_request(request=request, user=user)
{%- endif %}
        return api_response(data=response.data, http_status=response.status_code)


class AuthJwtRefreshApi(TokenRefreshView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    @extend_schema(
        tags=AUTH_TAGS,
        summary="JWT refresh",
        responses=envelope_serializer("AuthJwtRefreshEnvelope", AuthJwtRefreshOutputSerializer),
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return api_response(data=response.data, http_status=response.status_code)


class AuthJwtVerifyApi(TokenVerifyView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    @extend_schema(
        tags=AUTH_TAGS,
        summary="JWT verify",
        responses=envelope_serializer(
            "AuthJwtVerifyEnvelope",
            inline_serializer(name="AuthJwtVerifyResult", fields={}),
        ),
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return api_response(data=response.data, http_status=response.status_code)
