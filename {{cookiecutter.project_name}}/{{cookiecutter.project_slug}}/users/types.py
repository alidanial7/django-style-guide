from __future__ import annotations

from typing import Any, NotRequired, TypedDict


class RegisterData(TypedDict):
    """Validated payload for user registration (API → service)."""

{%- if cookiecutter.user_login_field == "username" %}
    username: str
{%- endif %}
    email: str
    password: str
    bio: NotRequired[str | None]
    avatar: NotRequired[Any]
{%- if cookiecutter.use_otp_login == "y" %}
    phone: NotRequired[str | None]
{%- endif %}


class ProfileUpdateData(TypedDict, total=False):
    """Partial profile PATCH — only keys present in the mapping were sent by the client."""

    bio: str | None
    avatar: Any
{%- if cookiecutter.use_otp_login == "y" %}
    phone: str | None
{%- endif %}


class ChangePasswordData(TypedDict):
    """Validated payload for password change."""

    current_password: str
    new_password: str
