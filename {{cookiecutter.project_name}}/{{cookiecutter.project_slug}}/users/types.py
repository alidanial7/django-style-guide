from __future__ import annotations

from typing import Any, NotRequired, TypedDict


class RegisterData(TypedDict):
    """Validated payload for user registration (API → service)."""

    email: str
    password: str
    bio: NotRequired[str | None]
    avatar: NotRequired[Any]


class ProfileUpdateData(TypedDict, total=False):
    """Partial profile PATCH — only keys present in the mapping were sent by the client."""

    bio: str | None
    avatar: Any


class ChangePasswordData(TypedDict):
    """Validated payload for password change."""

    current_password: str
    new_password: str
