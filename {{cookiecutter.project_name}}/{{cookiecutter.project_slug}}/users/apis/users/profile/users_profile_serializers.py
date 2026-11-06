from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from {{cookiecutter.project_slug}}.users.models import Profile
from {{cookiecutter.project_slug}}.users.selectors.users_selectors import get_avatar_url
{%- if cookiecutter.use_otp_login == "y" %}
from {{cookiecutter.project_slug}}.users.validators.phone import validate_phone
{%- endif %}


{%- if cookiecutter.use_otp_login == "y" %}
class UsersProfileOtpChallengeSerializer(serializers.Serializer):
    phone = serializers.CharField()
    expires_in = serializers.IntegerField()
    resend_in = serializers.IntegerField()
    test_mode = serializers.BooleanField()


class UsersProfilePendingOutputSerializer(serializers.Serializer):
    detail = serializers.CharField()
    otp = UsersProfileOtpChallengeSerializer()

{%- endif %}
class UsersProfileOutputSerializer(serializers.ModelSerializer):
{%- if cookiecutter.user_login_field == "username" %}
    username = serializers.CharField(source="user.username", read_only=True)
{%- endif %}
    email = serializers.EmailField(source="user.email", read_only=True)
{%- if cookiecutter.use_otp_login == "y" %}
    phone = serializers.CharField(
        source="user.phone",
        read_only=True,
        allow_null=True,
        help_text="Mobile as stored (98XXXXXXXXXX).",
    )
{%- endif %}
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
{%- if cookiecutter.user_login_field == "username" and cookiecutter.use_otp_login == "y" %}
        fields = ("username", "email", "phone", "bio", "avatar")
{%- elif cookiecutter.user_login_field == "username" %}
        fields = ("username", "email", "bio", "avatar")
{%- elif cookiecutter.use_otp_login == "y" %}
        fields = ("email", "phone", "bio", "avatar")
{%- else %}
        fields = ("email", "bio", "avatar")
{%- endif %}

    @extend_schema_field(serializers.URLField())
    def get_avatar(self, profile: Profile) -> str:
        return get_avatar_url(profile=profile, request=self.context.get("request"))


class UsersProfileUpdateInputSerializer(serializers.Serializer):
    bio = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=1000)
    avatar = serializers.ImageField(required=False, allow_null=True)
{%- if cookiecutter.use_otp_login == "y" %}
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=20,
        help_text=(
            "Optional new mobile. Profile changes are staged until "
            "POST /api/v1/auth/otp/verify/. OTP is sent to this number, or to the "
            "current phone when omitted. Avatar must be set in a later request."
        ),
    )

    def validate_phone(self, value):
        if value in (None, ""):
            return None
        try:
            return validate_phone(phone=value)
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages, code=error.code) from error
{%- endif %}
