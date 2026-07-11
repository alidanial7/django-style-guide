# Authentication

{%- if cookiecutter.use_jwt == "y" %}
This project was generated with **JWT** authentication (`djangorestframework-simplejwt` + token blacklist).
{%- else %}
This project was generated with **session** authentication.
{%- endif %}

The `users` app always provides register, profile, and password flows.

{%- if cookiecutter.use_jwt == "y" %}
## JWT

Login at `POST /api/v1/auth/jwt/login/` with `email` and `password`. Send the access token as `Authorization: Bearer …`.

Refresh tokens **rotate on every** `POST /api/v1/auth/jwt/refresh/` call: the response includes a new `access` and a new `refresh`. The previous refresh token is blacklisted and cannot be reused.

Logout with `POST /api/v1/auth/jwt/logout/` and body `{ "refresh": "<token>" }` to blacklist the refresh token.

| Endpoint | Auth | Notes |
|----------|------|-------|
| `POST /api/v1/auth/jwt/login/` | public | throttled (`auth`) |
| `POST /api/v1/auth/jwt/refresh/` | public | throttled (`auth`) |
| `POST /api/v1/auth/jwt/verify/` | public | throttled (`auth`) |
| `POST /api/v1/auth/jwt/logout/` | public | blacklists refresh token |
| `POST /api/v1/auth/password/change/` | JWT | current + new password |
| `POST /api/v1/auth/password/reset/` | public | emails reset uid/token (console backend locally) |
| `POST /api/v1/auth/password/reset/confirm/` | public | `{ uid, token, new_password, confirm_password }` |
| `POST /api/v1/users/register/` | public | throttled (`register`); returns tokens in output |
| `GET/PATCH /api/v1/users/profile/` | JWT | current user profile |

| Setting | Default | Env variable |
|---------|---------|--------------|
| Access token lifetime | 15 minutes | `JWT_ACCESS_TOKEN_LIFETIME_SECONDS` |
| Refresh token lifetime | 7 days | `JWT_REFRESH_TOKEN_LIFETIME_SECONDS` |

After upgrading, run `python manage.py migrate` to create the token blacklist tables.

Settings live in `config/settings/jwt.py`. Default DRF auth class: `JWTAuthentication` (`config/settings/drf.py`).
{%- else %}
## Session

Login at `POST /api/v1/auth/session/login/` with `email` and `password`. The server sets a session cookie.

Logout at `POST /api/v1/auth/session/logout/` (authenticated). Browser / cookie clients must send a valid CSRF token on unsafe methods (`POST`/`PATCH`/`PUT`/`DELETE`).

| Endpoint | Auth | Notes |
|----------|------|-------|
| `POST /api/v1/auth/session/login/` | public | throttled (`auth`) |
| `POST /api/v1/auth/session/logout/` | session | |
| `POST /api/v1/auth/password/change/` | session | current + new password |
| `POST /api/v1/auth/password/reset/` | public | emails reset uid/token (console backend locally) |
| `POST /api/v1/auth/password/reset/confirm/` | public | `{ uid, token, new_password, confirm_password }` |
| `POST /api/v1/users/register/` | public | creates user and logs them in |
| `GET/PATCH /api/v1/users/profile/` | session | current user profile |

Default DRF auth class: `SessionAuthentication` (`config/settings/drf.py`).
{%- endif %}

## Password reset email

Uses `EMAIL_*` / `DEFAULT_FROM_EMAIL` / `APP_DOMAIN` from `.env` (console backend by default in local). The service always succeeds for unknown emails (no account enumeration).

## Profile

A `Profile` (`bio`, `avatar`) is created automatically for every new user (signal). If no avatar is uploaded, the API returns the default static image at `/static/users/default_avatar.png`. Update with `PATCH /api/v1/users/profile/` (`multipart/form-data` for avatar uploads).

## Not included by design

Email verification, social login, and 2FA are intentionally omitted. Add them in the product layer when required.

## Implementation map

| Concern | Location |
|---------|----------|
| Login / logout / JWT views | `users/apis/auth/` |
| Password change / reset | `users/apis/auth/auth_password_apis.py` + `user_services` |
| Register | `users/apis/users/register/` |
| Profile | `users/apis/users/profile/` |
| Auth URLConf | `users/urls/auth.py` |
| User URLConf | `users/urls/users.py` |

See [Permissions](permissions.md) for how authenticated views opt in.
