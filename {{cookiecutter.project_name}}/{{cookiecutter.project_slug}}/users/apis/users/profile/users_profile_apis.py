from drf_spectacular.utils import extend_schema
from rest_framework import parsers
from rest_framework.views import APIView

from {{cookiecutter.project_slug}}.api.mixins import ApiAuthMixin
from {{cookiecutter.project_slug}}.common.http import api_response
from {{cookiecutter.project_slug}}.common.http.schema import envelope_serializer
from {{cookiecutter.project_slug}}.users.apis.users.profile.users_profile_serializers import (
    UsersProfileOutputSerializer,
    UsersProfileUpdateInputSerializer,
)
from {{cookiecutter.project_slug}}.users.constants import USERS_TAGS
from {{cookiecutter.project_slug}}.users.selectors.users_selectors import get_profile
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
        responses=envelope_serializer("UsersProfileUpdateEnvelope", UsersProfileOutputSerializer),
    )
    def patch(self, request):
        serializer = UsersProfileUpdateInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        profile = get_profile(user=request.user)
        profile = profile_update(
            profile=profile,
            bio=serializer.validated_data.get("bio"),
            avatar=serializer.validated_data.get("avatar"),
        )
        return api_response(data=UsersProfileOutputSerializer(profile, context={"request": request}).data)
