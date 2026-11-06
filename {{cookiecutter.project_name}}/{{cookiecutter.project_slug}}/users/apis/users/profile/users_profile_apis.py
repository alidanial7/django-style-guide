from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import parsers, status
from rest_framework.views import APIView

from {{cookiecutter.project_slug}}.api.mixins import ApiAuthMixin
from {{cookiecutter.project_slug}}.common.http import api_response
from {{cookiecutter.project_slug}}.common.http.schema import envelope_serializer
from {{cookiecutter.project_slug}}.users.apis.users.profile.users_profile_serializers import (
    UsersProfileOutputSerializer,
{%- if cookiecutter.use_otp_login == "y" %}
    UsersProfilePendingOutputSerializer,
{%- endif %}
    UsersProfileUpdateInputSerializer,
)
from {{cookiecutter.project_slug}}.users.constants import USERS_TAGS
from {{cookiecutter.project_slug}}.users.selectors.users_selectors import get_profile
{%- if cookiecutter.use_otp_login == "y" %}
from {{cookiecutter.project_slug}}.users.services.otp_services import (
    PENDING_PROFILE_UPDATE,
    request_otp,
)
{%- endif %}
from {{cookiecutter.project_slug}}.users.services.user_services import profile_update


class UsersProfileApi(ApiAuthMixin, APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    @extend_schema(
        tags=USERS_TAGS,
        summary="Current user",
        responses=envelope_serializer("UsersProfileEnvelope", UsersProfileOutputSerializer),
    )
    def get(self, request):
        profile = get_profile(user=request.user)
        return api_response(data=UsersProfileOutputSerializer(profile, context={"request": request}).data)

    @extend_schema(
        tags=USERS_TAGS,
        summary="Update current user profile",
        request=UsersProfileUpdateInputSerializer,
{%- if cookiecutter.use_otp_login == "y" %}
        responses={
            202: envelope_serializer(
                "UsersProfilePendingEnvelope", UsersProfilePendingOutputSerializer
            ),
        },
{%- else %}
        responses=envelope_serializer("UsersProfileUpdateEnvelope", UsersProfileOutputSerializer),
{%- endif %}
    )
    def patch(self, request):
        serializer = UsersProfileUpdateInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        profile = get_profile(user=request.user)
{%- if cookiecutter.use_otp_login == "y" %}
        if data.get("avatar") is not None:
            raise DjangoValidationError(
                {"avatar": _("set avatar after phone verification.")}
            )

        challenge_phone = data.get("phone") or profile.user.phone
        if not challenge_phone:
            raise DjangoValidationError(
                {
                    "phone": _(
                        "phone is required to update profile when OTP auth is enabled."
                    )
                }
            )

        pending_data = {key: data[key] for key in data if key != "avatar"}
        otp_challenge = request_otp(
            phone=challenge_phone,
            pending={
                "kind": PENDING_PROFILE_UPDATE,
                "user_id": str(profile.user.pk),
                "data": pending_data,
            },
        )
        return api_response(
            data=UsersProfilePendingOutputSerializer(
                {"detail": "otp_required", "otp": otp_challenge}
            ).data,
            http_status=status.HTTP_202_ACCEPTED,
        )
{%- else %}
        profile = profile_update(profile=profile, data=data)
        return api_response(data=UsersProfileOutputSerializer(profile, context={"request": request}).data)
{%- endif %}
