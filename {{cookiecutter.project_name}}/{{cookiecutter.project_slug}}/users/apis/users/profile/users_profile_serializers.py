from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from {{cookiecutter.project_slug}}.users.models import Profile
from {{cookiecutter.project_slug}}.users.selector.users_selectors import get_avatar_url


class UsersProfileOutputSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ("email", "bio", "avatar")

    @extend_schema_field(serializers.URLField())
    def get_avatar(self, profile: Profile) -> str:
        return get_avatar_url(profile=profile, request=self.context.get("request"))


class UsersProfileUpdateInputSerializer(serializers.Serializer):
    bio = serializers.CharField(max_length=1000, required=False, allow_blank=True, allow_null=True)
    avatar = serializers.ImageField(required=False, allow_null=True)
