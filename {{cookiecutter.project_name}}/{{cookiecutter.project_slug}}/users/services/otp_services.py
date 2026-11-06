from __future__ import annotations

import hashlib
import secrets
import time
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils.translation import gettext_lazy as _

from {{cookiecutter.project_slug}}.common.db.integrity import map_integrity_error
from {{cookiecutter.project_slug}}.users.errors.codes import UserErrorCode
from {{cookiecutter.project_slug}}.users.models import BaseUser, Profile
from {{cookiecutter.project_slug}}.users.providers.sms import get_sms_provider
from {{cookiecutter.project_slug}}.users.types import ProfileUpdateData, RegisterData
from {{cookiecutter.project_slug}}.users.validators.phone import validate_phone

_CHALLENGE_KEY = "otp:challenge:{phone}"
_COOLDOWN_KEY = "otp:cooldown:{phone}"

PENDING_REGISTER = "register"
PENDING_PROFILE_UPDATE = "profile_update"


def _challenge_key(*, phone: str) -> str:
    return _CHALLENGE_KEY.format(phone=phone)


def _cooldown_key(*, phone: str) -> str:
    return _COOLDOWN_KEY.format(phone=phone)


def _hash_code(*, code: str) -> str:
    material = f"{code}:{settings.SECRET_KEY}".encode()
    return hashlib.sha256(material).hexdigest()


def _generate_code() -> str:
    if getattr(settings, "OTP_TEST", False):
        return settings.OTP_TEST_CODE
    length = int(getattr(settings, "OTP_CODE_LENGTH", 5))
    upper = 10**length
    return f"{secrets.randbelow(upper):0{length}d}"


def request_otp(*, phone: str, pending: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Create (or replace) an OTP challenge and deliver SMS unless ``OTP_TEST``.

    Optional ``pending`` is applied only after a successful ``verify_otp``::

        {"kind": "register", "data": {...}}
        {"kind": "profile_update", "user_id": "<pk>", "data": {...}}

    Public response never includes the code — use ``OTP_TEST=true`` locally
    and enter ``OTP_TEST_CODE`` (default ``12345``).
    """
    normalized = validate_phone(phone=phone)

    cooldown = int(getattr(settings, "OTP_RESEND_SECONDS", 60))
    if cache.get(_cooldown_key(phone=normalized)):
        raise ValidationError(
            _("Please wait before requesting another code."),
            code=UserErrorCode.OTP_RESEND_COOLDOWN,
        )

    code = _generate_code()
    ttl = int(getattr(settings, "OTP_TTL_SECONDS", 120))
    payload: dict[str, Any] = {
        "code_hash": _hash_code(code=code),
        "attempts": 0,
        "expires_at": time.time() + ttl,
    }
    if pending is not None:
        payload["pending"] = pending

    cache.set(_challenge_key(phone=normalized), payload, timeout=ttl)
    cache.set(_cooldown_key(phone=normalized), True, timeout=cooldown)

    if not getattr(settings, "OTP_TEST", False):
        message = _("Your verification code is {code}.").format(code=code)
        get_sms_provider().send_otp(phone=normalized, message=str(message))

    return {
        "phone": normalized,
        "expires_in": ttl,
        "resend_in": cooldown,
        "test_mode": bool(getattr(settings, "OTP_TEST", False)),
    }


@transaction.atomic
def verify_otp(*, phone: str, code: str) -> BaseUser:
    """
    Validate OTP, then:

    - pending ``register`` → create the staged account
    - pending ``profile_update`` → apply the staged profile PATCH
    - otherwise → get-or-create user by phone (OTP login)
    """
    normalized = validate_phone(phone=phone)
    raw_code = (code or "").strip()

    payload = cache.get(_challenge_key(phone=normalized))
    if not payload:
        raise ValidationError(
            _("Verification code expired or not requested."),
            code=UserErrorCode.OTP_EXPIRED,
        )

    expires_at = float(payload.get("expires_at", 0))
    if expires_at and time.time() > expires_at:
        cache.delete(_challenge_key(phone=normalized))
        raise ValidationError(
            _("Verification code expired or not requested."),
            code=UserErrorCode.OTP_EXPIRED,
        )

    attempts = int(payload.get("attempts", 0))
    max_attempts = int(getattr(settings, "OTP_MAX_ATTEMPTS", 5))
    if attempts >= max_attempts:
        cache.delete(_challenge_key(phone=normalized))
        raise ValidationError(
            _("Too many invalid attempts. Request a new code."),
            code=UserErrorCode.OTP_TOO_MANY_ATTEMPTS,
        )

    if _hash_code(code=raw_code) != payload.get("code_hash"):
        payload["attempts"] = attempts + 1
        remaining = max(int(expires_at - time.time()), 1)
        cache.set(_challenge_key(phone=normalized), payload, timeout=remaining)
        raise ValidationError(
            _("Invalid verification code."),
            code=UserErrorCode.OTP_INVALID,
        )

    pending = payload.get("pending")
    cache.delete(_challenge_key(phone=normalized))
    cache.delete(_cooldown_key(phone=normalized))

    if not pending:
        return _get_or_create_user_by_phone(phone=normalized)

    kind = pending.get("kind")
    if kind == PENDING_REGISTER:
        return _complete_pending_register(phone=normalized, data=pending.get("data") or {})
    if kind == PENDING_PROFILE_UPDATE:
        return _complete_pending_profile_update(
            phone=normalized,
            user_id=pending.get("user_id"),
            data=pending.get("data") or {},
        )

    raise ValidationError(
        _("Invalid verification challenge."),
        code=UserErrorCode.OTP_INVALID,
    )


def _complete_pending_register(*, phone: str, data: dict[str, Any]) -> BaseUser:
    from {{cookiecutter.project_slug}}.users.services.user_services import register

    existing = BaseUser.objects.filter(phone=phone).first()
    if existing is not None:
        if not existing.is_active:
            raise ValidationError(
                _("This account is inactive."),
                code=UserErrorCode.ACCOUNT_INACTIVE,
            )
        return existing

    register_data: RegisterData = {
{%- if cookiecutter.user_login_field == "username" %}
        "username": data["username"],
{%- endif %}
        "email": data["email"],
        "password": data["password"],
        "phone": phone,
    }
    if data.get("bio") is not None:
        register_data["bio"] = data.get("bio")
    return register(data=register_data)


def _complete_pending_profile_update(
    *,
    phone: str,
    user_id: Any,
    data: dict[str, Any],
) -> BaseUser:
    from {{cookiecutter.project_slug}}.users.services.user_services import profile_update

    if user_id is None:
        raise ValidationError(
            _("Invalid verification challenge."),
            code=UserErrorCode.OTP_INVALID,
        )

    try:
        user = BaseUser.objects.get(pk=user_id)
    except BaseUser.DoesNotExist as error:
        raise ValidationError(
            _("Invalid verification challenge."),
            code=UserErrorCode.OTP_INVALID,
        ) from error

    if not user.is_active:
        raise ValidationError(
            _("This account is inactive."),
            code=UserErrorCode.ACCOUNT_INACTIVE,
        )

    update_data: ProfileUpdateData = {}
    if "bio" in data:
        update_data["bio"] = data.get("bio")
    if "phone" in data:
        # May be a new number (matches verified ``phone``) or ``None`` to clear.
        update_data["phone"] = data.get("phone")

    profile = Profile.objects.select_related("user").get(user=user)
    if update_data:
        profile_update(profile=profile, data=update_data)
    user.refresh_from_db()
    return user


def _get_or_create_user_by_phone(*, phone: str) -> BaseUser:
    existing = BaseUser.objects.filter(phone=phone).first()
    if existing is not None:
        if not existing.is_active:
            raise ValidationError(
                _("This account is inactive."),
                code=UserErrorCode.ACCOUNT_INACTIVE,
            )
        return existing

    try:
{%- if cookiecutter.user_login_field == "username" %}
        user = BaseUser.objects.create_user(
            username=phone,
            email=f"{phone}@otp.local",
            password=None,
            phone=phone,
        )
{%- else %}
        user = BaseUser.objects.create_user(
            email=f"{phone}@otp.local",
            password=None,
            phone=phone,
        )
{%- endif %}
    except IntegrityError as error:
        map_integrity_error(error, model=BaseUser)
        raise

    return user
