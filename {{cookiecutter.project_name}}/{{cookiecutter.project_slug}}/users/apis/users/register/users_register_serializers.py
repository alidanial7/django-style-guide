from drf_spectacular.utils import extend_schema_field
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from {{cookiecutter.project_slug}}.common.errors.codes import ErrorCode
from {{cookiecutter.project_slug}}.users.errors.codes import UserErrorCode
from {{cookiecutter.project_slug}}.users.models import BaseUser
from {{cookiecutter.project_slug}}.users.selector.users_selectors import get_avatar_url
from {{cookiecutter.project_slug}}.users.validators.password import PASSWORD_VALIDATORS


class UsersRegisterInputSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    bio = serializers.CharField(max_length=1000, required=False, allow_blank=True, allow_null=True)
    avatar = serializers.ImageField(required=False, allow_null=True)
    password = serializers.CharField(validators=PASSWORD_VALIDATORS)
    confirm_password = serializers.CharField(max_length=255)

    def validate(self, data):
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if not password or not confirm_password:
            raise serializers.ValidationError(
                {"non_field_errors": [_("please fill password and confirm password")]},
                code=ErrorCode.REQUIRED,
            )

        if password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": [_("confirm password is not equal to password")]},
                code=UserErrorCode.PASSWORD_MISMATCH,
            )
        return data

class UsersRegisterOutputSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField("get_token")
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = BaseUser
        fields = ("email", "avatar", "token", "created_at", "updated_at")

    @extend_schema_field(
        serializers.DictField(
            child=serializers.CharField(),
            help_text="JWT refresh and access tokens",
        )
    )
    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    @extend_schema_field(serializers.URLField())
    def get_avatar(self, user: BaseUser) -> str:
        return get_avatar_url(profile=user.profile, request=self.context.get("request"))
