{% if cookiecutter.use_jwt != "y" -%}
from django.contrib.auth import login
{% endif -%}
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import parsers, status
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from {{cookiecutter.project_slug}}.common.http import api_response
from {{cookiecutter.project_slug}}.common.http.schema import envelope_serializer
from {{cookiecutter.project_slug}}.users.apis.users.register.users_register_serializers import (
    UsersRegisterInputSerializer,
    UsersRegisterOutputSerializer,
{%- if cookiecutter.use_otp_login == "y" %}
    UsersRegisterPendingOutputSerializer,
{%- endif %}
)
from {{cookiecutter.project_slug}}.users.constants import USERS_TAGS
{%- if cookiecutter.use_otp_login == "y" %}
from {{cookiecutter.project_slug}}.users.services.otp_services import PENDING_REGISTER, request_otp
{%- endif %}
from {{cookiecutter.project_slug}}.users.services.user_services import register


class UsersRegisterApi(APIView):
    permission_classes = [AllowAny]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"

    @extend_schema(
        tags=USERS_TAGS,
        summary="Register a new user",
        request=UsersRegisterInputSerializer,
{%- if cookiecutter.use_otp_login == "y" %}
        responses={
            202: envelope_serializer(
                "UsersRegisterPendingEnvelope", UsersRegisterPendingOutputSerializer
            ),
        },
{%- else %}
        responses={201: envelope_serializer("UsersRegisterEnvelope", UsersRegisterOutputSerializer)},
{%- endif %}
    )
    def post(self, request):
        serializer = UsersRegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
{%- if cookiecutter.use_otp_login == "y" %}
        if data.get("avatar") is not None:
            raise DjangoValidationError(
                {"avatar": _("set avatar after phone verification.")}
            )
        # Stage account in OTP challenge; commit on POST /auth/otp/verify/.
        pending_data = {
{%- if cookiecutter.user_login_field == "username" %}
            "username": data["username"],
{%- endif %}
            "email": data["email"],
            "password": data["password"],
            "phone": data["phone"],
        }
        if "bio" in data:
            pending_data["bio"] = data.get("bio")
        otp_challenge = request_otp(
            phone=data["phone"],
            pending={"kind": PENDING_REGISTER, "data": pending_data},
        )
        return api_response(
            data=UsersRegisterPendingOutputSerializer(
                {"detail": "otp_required", "otp": otp_challenge}
            ).data,
            http_status=status.HTTP_202_ACCEPTED,
        )
{%- else %}
        user = register(data=data)
{%- if cookiecutter.use_jwt != "y" %}
        login(request, user)
{%- endif %}
        return api_response(
            data=UsersRegisterOutputSerializer(user, context={"request": request}).data,
            http_status=status.HTTP_201_CREATED,
        )
{%- endif %}
