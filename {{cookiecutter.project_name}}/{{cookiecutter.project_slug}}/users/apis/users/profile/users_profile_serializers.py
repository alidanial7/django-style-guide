from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from {{cookiecutter.project_slug}}.users.models import Profile
from {{cookiecutter.project_slug}}.users.selectors.users_selectors import get_avatar_url


class UsersProfileOutputSerializer(serializers.ModelSerializer):
{%- if cookiecutter.user_login_field == "username" %}
    username = serializers.CharField(source="user.username", read_only=True)
{%- endif %}
    email = serializers.EmailField(source="user.email", read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
{%- if cookiecutter.user_login_field == "username" %}
        fields = ("username", "email", "bio", "avatar")
{%- else %}
        fields = ("email", "bio", "avatar")
{%- endif %}

    @extend_schema_field(serializers.URLField())
    def get_avatar(self, profile: Profile) -> str:
        return get_avatar_url(profile=profile, request=self.context.get("request"))


class UsersProfileInputSerializer(serializers.Serializer):
    bio = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=1000)
    avatar = serializers.ImageField(required=False, allow_null=True)
