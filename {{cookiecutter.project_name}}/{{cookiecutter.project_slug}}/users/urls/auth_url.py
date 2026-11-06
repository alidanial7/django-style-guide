from django.urls import path

{% if cookiecutter.use_jwt == "y" %}
from {{cookiecutter.project_slug}}.users.apis.auth.auth_jwt_apis import (
    AuthJwtLoginApi,
    AuthJwtRefreshApi,
    AuthJwtVerifyApi,
)
from {{cookiecutter.project_slug}}.users.apis.auth.auth_logout_apis import AuthLogoutApi
{% if cookiecutter.use_otp_login == "y" %}
from {{cookiecutter.project_slug}}.users.apis.auth.auth_otp_apis import AuthOtpRequestApi, AuthOtpVerifyApi
{% endif %}
from {{cookiecutter.project_slug}}.users.apis.auth.auth_password_apis import (
    AuthPasswordChangeApi,
    AuthPasswordResetConfirmApi,
    AuthPasswordResetRequestApi,
)
{% if cookiecutter.use_google_login == "y" or cookiecutter.use_microsoft_login == "y" or cookiecutter.use_apple_login == "y" %}
from {{cookiecutter.project_slug}}.users.apis.auth.auth_social_apis import (
{% if cookiecutter.use_apple_login == "y" %}
    AuthAppleLoginApi,
{% endif %}
{% if cookiecutter.use_google_login == "y" %}
    AuthGoogleLoginApi,
{% endif %}
{% if cookiecutter.use_microsoft_login == "y" %}
    AuthMicrosoftLoginApi,
{% endif %}
)
{% endif %}
{% elif cookiecutter.use_otp_login == "y" %}
from {{cookiecutter.project_slug}}.users.apis.auth.auth_otp_apis import AuthOtpRequestApi, AuthOtpVerifyApi
from {{cookiecutter.project_slug}}.users.apis.auth.auth_password_apis import (
    AuthPasswordChangeApi,
    AuthPasswordResetConfirmApi,
    AuthPasswordResetRequestApi,
)
from {{cookiecutter.project_slug}}.users.apis.auth.auth_session_apis import (
    AuthSessionLoginApi,
    AuthSessionLogoutApi,
)
{% if cookiecutter.use_google_login == "y" or cookiecutter.use_microsoft_login == "y" or cookiecutter.use_apple_login == "y" %}
from {{cookiecutter.project_slug}}.users.apis.auth.auth_social_apis import (
{% if cookiecutter.use_apple_login == "y" %}
    AuthAppleLoginApi,
{% endif %}
{% if cookiecutter.use_google_login == "y" %}
    AuthGoogleLoginApi,
{% endif %}
{% if cookiecutter.use_microsoft_login == "y" %}
    AuthMicrosoftLoginApi,
{% endif %}
)
{% endif %}
{% else %}
from {{cookiecutter.project_slug}}.users.apis.auth.auth_password_apis import (
    AuthPasswordChangeApi,
    AuthPasswordResetConfirmApi,
    AuthPasswordResetRequestApi,
)
from {{cookiecutter.project_slug}}.users.apis.auth.auth_session_apis import (
    AuthSessionLoginApi,
    AuthSessionLogoutApi,
)
{% if cookiecutter.use_google_login == "y" or cookiecutter.use_microsoft_login == "y" or cookiecutter.use_apple_login == "y" %}
from {{cookiecutter.project_slug}}.users.apis.auth.auth_social_apis import (
{% if cookiecutter.use_apple_login == "y" %}
    AuthAppleLoginApi,
{% endif %}
{% if cookiecutter.use_google_login == "y" %}
    AuthGoogleLoginApi,
{% endif %}
{% if cookiecutter.use_microsoft_login == "y" %}
    AuthMicrosoftLoginApi,
{% endif %}
)
{% endif %}
{% endif %}

app_name = "auth"

urlpatterns = [
{% if cookiecutter.use_jwt == "y" %}
    path("jwt/login/", AuthJwtLoginApi.as_view(), name="login"),
    path("jwt/refresh/", AuthJwtRefreshApi.as_view(), name="refresh"),
    path("jwt/verify/", AuthJwtVerifyApi.as_view(), name="verify"),
    path("jwt/logout/", AuthLogoutApi.as_view(), name="logout"),
{% else %}
    path("session/login/", AuthSessionLoginApi.as_view(), name="login"),
    path("session/logout/", AuthSessionLogoutApi.as_view(), name="logout"),
{% endif %}
{% if cookiecutter.use_otp_login == "y" %}
    path("otp/request/", AuthOtpRequestApi.as_view(), name="otp-request"),
    path("otp/verify/", AuthOtpVerifyApi.as_view(), name="otp-verify"),
{% endif %}
{% if cookiecutter.use_google_login == "y" %}
    path("social/google/", AuthGoogleLoginApi.as_view(), name="social-google"),
{% endif %}
{% if cookiecutter.use_microsoft_login == "y" %}
    path("social/microsoft/", AuthMicrosoftLoginApi.as_view(), name="social-microsoft"),
{% endif %}
{% if cookiecutter.use_apple_login == "y" %}
    path("social/apple/", AuthAppleLoginApi.as_view(), name="social-apple"),
{% endif %}
    path("password/change/", AuthPasswordChangeApi.as_view(), name="password-change"),
    path("password/reset/", AuthPasswordResetRequestApi.as_view(), name="password-reset"),
    path(
        "password/reset/confirm/",
        AuthPasswordResetConfirmApi.as_view(),
        name="password-reset-confirm",
    ),
]
