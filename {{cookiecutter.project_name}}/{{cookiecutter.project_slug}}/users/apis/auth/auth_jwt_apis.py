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
    """Obtain pair; field name follows USERNAME_FIELD (email) for schema + clients."""


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
