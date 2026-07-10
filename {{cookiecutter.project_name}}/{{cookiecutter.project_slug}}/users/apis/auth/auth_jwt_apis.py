from drf_spectacular.utils import extend_schema
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from {{cookiecutter.project_slug}}.common.http import api_response
from {{cookiecutter.project_slug}}.users.constants import AUTH_TAGS


class AuthJwtLoginApi(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    @extend_schema(tags=AUTH_TAGS, summary="JWT login")
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return api_response(data=response.data, http_status=response.status_code)


class AuthJwtRefreshApi(TokenRefreshView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    @extend_schema(tags=AUTH_TAGS, summary="JWT refresh")
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return api_response(data=response.data, http_status=response.status_code)


class AuthJwtVerifyApi(TokenVerifyView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    @extend_schema(tags=AUTH_TAGS, summary="JWT verify")
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return api_response(data=response.data, http_status=response.status_code)
