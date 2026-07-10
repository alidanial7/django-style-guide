from django.core.validators import MinLengthValidator
from drf_spectacular.utils import extend_schema, extend_schema_field
from rest_framework import parsers, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from {{cookiecutter.project_slug}}.api.mixins import ApiAuthMixin
from {{cookiecutter.project_slug}}.users.models import BaseUser, Profile
from {{cookiecutter.project_slug}}.users.selectors import get_avatar_url, get_profile
from {{cookiecutter.project_slug}}.users.services import profile_update, register

from .validators import letter_validator, number_validator, special_char_validator


class ProfileApi(ApiAuthMixin, APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    class OutPutSerializer(serializers.ModelSerializer):
        email = serializers.EmailField(source="user.email", read_only=True)
        avatar = serializers.SerializerMethodField()

        class Meta:
            model = Profile
            fields = ("email", "bio", "avatar")

        @extend_schema_field(serializers.URLField())
        def get_avatar(self, profile: Profile) -> str:
            return get_avatar_url(profile=profile, request=self.context.get("request"))

    class InputUpdateSerializer(serializers.Serializer):
        bio = serializers.CharField(max_length=1000, required=False, allow_blank=True, allow_null=True)
        avatar = serializers.ImageField(required=False, allow_null=True)

    @extend_schema(
        tags=["users"],
        summary="Current user",
        responses=OutPutSerializer,
    )
    def get(self, request):
        profile = get_profile(user=request.user)
        return Response(self.OutPutSerializer(profile, context={"request": request}).data)

    @extend_schema(
        tags=["users"],
        summary="Update current user profile",
        request=InputUpdateSerializer,
        responses=OutPutSerializer,
    )
    def patch(self, request):
        serializer = self.InputUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        profile = get_profile(user=request.user)
        profile = profile_update(
            profile=profile,
            bio=serializer.validated_data.get("bio"),
            avatar=serializer.validated_data.get("avatar"),
        )
        return Response(self.OutPutSerializer(profile, context={"request": request}).data)


class RegisterApi(APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    class InputRegisterSerializer(serializers.Serializer):
        email = serializers.EmailField(max_length=255)
        bio = serializers.CharField(max_length=1000, required=False, allow_blank=True, allow_null=True)
        avatar = serializers.ImageField(required=False, allow_null=True)
        password = serializers.CharField(
            validators=[number_validator, letter_validator, special_char_validator, MinLengthValidator(limit_value=10)]
        )
        confirm_password = serializers.CharField(max_length=255)

        def validate_email(self, email):
            if BaseUser.objects.filter(email=email).exists():
                raise serializers.ValidationError("email Already Taken")
            return email

        def validate(self, data):
            if not data.get("password") or not data.get("confirm_password"):
                raise serializers.ValidationError("Please fill password and confirm password")

            if data.get("password") != data.get("confirm_password"):
                raise serializers.ValidationError("confirm password is not equal to password")
            return data

    class OutPutRegisterSerializer(serializers.ModelSerializer):
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
            data = {}
            token_class = RefreshToken

            refresh = token_class.for_user(user)

            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)

            return data

        @extend_schema_field(serializers.URLField())
        def get_avatar(self, user: BaseUser) -> str:
            return get_avatar_url(profile=user.profile, request=self.context.get("request"))

    @extend_schema(
        tags=["users"],
        summary="Register a new user",
        request=InputRegisterSerializer,
        responses=OutPutRegisterSerializer,
    )
    def post(self, request):
        serializer = self.InputRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = register(
                email=serializer.validated_data.get("email"),
                password=serializer.validated_data.get("password"),
                bio=serializer.validated_data.get("bio"),
                avatar=serializer.validated_data.get("avatar"),
            )
        except Exception as ex:
            return Response({"detail": f"database error: {ex}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.OutPutRegisterSerializer(user, context={"request": request}).data)
