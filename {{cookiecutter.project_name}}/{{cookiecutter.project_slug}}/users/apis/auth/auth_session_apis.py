from django.contrib.auth import authenticate, login, logout
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from {{cookiecutter.project_slug}}.api.mixins import ApiAuthMixin
from {{cookiecutter.project_slug}}.common.errors.codes import ErrorCode
from {{cookiecutter.project_slug}}.common.http import api_response
from {{cookiecutter.project_slug}}.users.constants import AUTH_TAGS


class AuthSessionLoginInputSerializer(serializers.Serializer):
{%- if cookiecutter.user_login_field == "username" %}
    username = serializers.CharField()
{%- else %}
    email = serializers.EmailField()
{%- endif %}
    password = serializers.CharField()


class AuthSessionLoginApi(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    @extend_schema(
        tags=AUTH_TAGS,
        summary="Session login",
        request=AuthSessionLoginInputSerializer,
    )
    def post(self, request):
        serializer = AuthSessionLoginInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
{%- if cookiecutter.user_login_field == "username" %}
        login_value = serializer.validated_data["username"]
{%- else %}
        login_value = serializer.validated_data["email"]
{%- endif %}
        user = authenticate(
            request,
            username=login_value,
            password=serializer.validated_data["password"],
        )
        if user is None:
            raise serializers.ValidationError(
                {"non_field_errors": [_("unable to log in with provided credentials.")]},
                code=ErrorCode.INVALID,
            )
        login(request, user)
{%- if cookiecutter.user_login_field == "username" %}
        return api_response(data={"username": user.username, "email": user.email})
{%- else %}
        return api_response(data={"email": user.email})
{%- endif %}


class AuthSessionLogoutApi(ApiAuthMixin, APIView):
    @extend_schema(tags=AUTH_TAGS, summary="Session logout")
    def post(self, request):
        logout(request)
        return api_response(data={"detail": "logged out."})
