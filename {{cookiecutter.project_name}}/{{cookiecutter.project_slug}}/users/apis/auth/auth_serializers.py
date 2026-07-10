from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from {{cookiecutter.project_slug}}.users.errors.codes import UserErrorCode
from {{cookiecutter.project_slug}}.users.validators.password import PASSWORD_VALIDATORS


{%- if cookiecutter.use_jwt == "y" %}
class AuthLogoutInputSerializer(serializers.Serializer):
    refresh = serializers.CharField()


{%- endif %}
class AuthPasswordChangeInputSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField(validators=PASSWORD_VALIDATORS)
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": [_("confirm password is not equal to password")]},
                code=UserErrorCode.PASSWORD_MISMATCH,
            )
        return data


class AuthPasswordResetRequestInputSerializer(serializers.Serializer):
    email = serializers.EmailField()


class AuthPasswordResetConfirmInputSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(validators=PASSWORD_VALIDATORS)
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": [_("confirm password is not equal to password")]},
                code=UserErrorCode.PASSWORD_MISMATCH,
            )
        return data
