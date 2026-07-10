from django.urls import path

from {{cookiecutter.project_slug}}.users.apis.auth.auth_jwt_apis import (
    AuthJwtLoginApi,
    AuthJwtRefreshApi,
    AuthJwtVerifyApi,
)
from {{cookiecutter.project_slug}}.users.apis.auth.auth_logout_apis import AuthLogoutApi
from {{cookiecutter.project_slug}}.users.apis.auth.auth_password_apis import (
    AuthPasswordChangeApi,
    AuthPasswordResetConfirmApi,
    AuthPasswordResetRequestApi,
)

app_name = "auth"

urlpatterns = [
    path("jwt/login/", AuthJwtLoginApi.as_view(), name="login"),
    path("jwt/refresh/", AuthJwtRefreshApi.as_view(), name="refresh"),
    path("jwt/verify/", AuthJwtVerifyApi.as_view(), name="verify"),
    path("jwt/logout/", AuthLogoutApi.as_view(), name="logout"),
    path("password/change/", AuthPasswordChangeApi.as_view(), name="password-change"),
    path("password/reset/", AuthPasswordResetRequestApi.as_view(), name="password-reset"),
    path(
        "password/reset/confirm/",
        AuthPasswordResetConfirmApi.as_view(),
        name="password-reset-confirm",
    ),
]
