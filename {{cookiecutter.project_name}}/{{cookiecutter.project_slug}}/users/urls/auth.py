from django.urls import path

{%- if cookiecutter.use_jwt == "y" %}
from {{cookiecutter.project_slug}}.users.apis.auth.auth_jwt_apis import (
    AuthJwtLoginApi,
    AuthJwtRefreshApi,
    AuthJwtVerifyApi,
)
from {{cookiecutter.project_slug}}.users.apis.auth.auth_logout_apis import AuthLogoutApi
{%- else %}
from {{cookiecutter.project_slug}}.users.apis.auth.auth_session_apis import (
    AuthSessionLoginApi,
    AuthSessionLogoutApi,
)
{%- endif %}
from {{cookiecutter.project_slug}}.users.apis.auth.auth_password_apis import (
    AuthPasswordChangeApi,
    AuthPasswordResetConfirmApi,
    AuthPasswordResetRequestApi,
)

app_name = "auth"

urlpatterns = [
{%- if cookiecutter.use_jwt == "y" %}
    path("jwt/login/", AuthJwtLoginApi.as_view(), name="login"),
    path("jwt/refresh/", AuthJwtRefreshApi.as_view(), name="refresh"),
    path("jwt/verify/", AuthJwtVerifyApi.as_view(), name="verify"),
    path("jwt/logout/", AuthLogoutApi.as_view(), name="logout"),
{%- else %}
    path("session/login/", AuthSessionLoginApi.as_view(), name="login"),
    path("session/logout/", AuthSessionLogoutApi.as_view(), name="logout"),
{%- endif %}
    path("password/change/", AuthPasswordChangeApi.as_view(), name="password-change"),
    path("password/reset/", AuthPasswordResetRequestApi.as_view(), name="password-reset"),
    path(
        "password/reset/confirm/",
        AuthPasswordResetConfirmApi.as_view(),
        name="password-reset-confirm",
    ),
]
