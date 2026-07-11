from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from {{cookiecutter.project_slug}}.common.http import api_response
from {{cookiecutter.project_slug}}.users.apis.auth.auth_serializers import AuthLogoutInputSerializer
from {{cookiecutter.project_slug}}.users.constants import AUTH_TAGS
from {{cookiecutter.project_slug}}.users.services.user_services import logout


class AuthLogoutApi(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    @extend_schema(
        tags=AUTH_TAGS,
        summary="Logout (blacklist refresh token)",
        request=AuthLogoutInputSerializer,
    )
    def post(self, request):
        serializer = AuthLogoutInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        logout(refresh_token=serializer.validated_data["refresh"])
        return api_response(data={"detail": "logged out."})
