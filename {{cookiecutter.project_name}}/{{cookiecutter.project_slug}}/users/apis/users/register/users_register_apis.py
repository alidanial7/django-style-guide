from drf_spectacular.utils import extend_schema
from rest_framework import parsers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from {{cookiecutter.project_slug}}.users.apis.users.register.users_register_serializers import (
    UsersRegisterInputSerializer,
    UsersRegisterOutputSerializer,
)
from {{cookiecutter.project_slug}}.users.constants import USERS_TAGS
from {{cookiecutter.project_slug}}.users.services.user_services import register


class UsersRegisterApi(APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    @extend_schema(
        tags=USERS_TAGS,
        summary="Register a new user",
        request=UsersRegisterInputSerializer,
        responses=UsersRegisterOutputSerializer,
    )
    def post(self, request):
        serializer = UsersRegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = register(
            email=serializer.validated_data.get("email"),
            password=serializer.validated_data.get("password"),
            bio=serializer.validated_data.get("bio"),
            avatar=serializer.validated_data.get("avatar"),
        )
        return Response(
            UsersRegisterOutputSerializer(user, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )
