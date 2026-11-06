from __future__ import annotations

import hashlib
import secrets
import time
from typing import Any

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils.translation import gettext_lazy as _

from {{cookiecutter.project_slug}}.common.db.integrity import map_integrity_error
from {{cookiecutter.project_slug}}.common.services import model_save
from {{cookiecutter.project_slug}}.users.errors.codes import UserErrorCode
from {{cookiecutter.project_slug}}.users.models import BaseUser, Profile
from {{cookiecutter.project_slug}}.users.providers.sms import get_sms_provider
from {{cookiecutter.project_slug}}.users.types import ProfileUpdateData
from {{cookiecutter.project_slug}}.users.validators.phone import validate_phone

KIND_LOGIN = "login"
KIND_REGISTER = "register"
KIND_PROFILE_UPDATE = "profile_update"

PENDING_REGISTER = KIND_REGISTER
PENDING_PROFILE_UPDATE = KIND_PROFILE_UPDATE

_CHALLENGE_KEY = "otp:challenge:{kind}:{phone}"
_COOLDOWN_KEY = "otp:cooldown:{kind}:{phone}"


def _challenge_key(*, phone: str, kind: str) -> str:
    return _CHALLENGE_KEY.format(kind=kind, phone=phone)


def _cooldown_key(*, phone: str, kind: str) -> str:
    return _COOLDOWN_KEY.format(kind=kind, phone=phone)


def _hash_code(*, code: str) -> str:
    material = f"{code}:{settings.SECRET_KEY}".encode()
    return hashlib.sha256(material).hexdigest()


def _generate_code() -> str:
    if getattr(settings, "OTP_TEST", False):
        return settings.OTP_TEST_CODE
    length = int(getattr(settings, "OTP_CODE_LENGTH", 5))
    upper = 10**length
    return f"{secrets.randbelow(upper):0{length}d}"


def request_otp(
    *,
    phone: str,
    kind: str = KIND_LOGIN,
    pending: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create (or replace) an OTP challenge for ``kind`` and deliver SMS unless ``OTP_TEST``.

    Challenges are namespaced by kind so login / register / profile_update do not
    overwrite each other. Optional ``pending`` is applied only after ``verify_otp``.
    """
    if kind not in {KIND_LOGIN, KIND_REGISTER, KIND_PROFILE_UPDATE}:
        raise ValidationError(
            _("Invalid verification challenge."),
            code=UserErrorCode.OTP_INVALID,
        )

    normalized = validate_phone(phone=phone)

    cooldown = int(getattr(settings, "OTP_RESEND_SECONDS", 60))
    if cache.get(_cooldown_key(phone=normalized, kind=kind)):
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
        "kind": kind,
    }
    if pending is not None:
        payload["pending"] = pending

    cache.set(_challenge_key(phone=normalized, kind=kind), payload, timeout=ttl)
    cache.set(_cooldown_key(phone=normalized, kind=kind), True, timeout=cooldown)

    if not getattr(settings, "OTP_TEST", False):
        message = _("Your verification code is {code}.").format(code=code)
        get_sms_provider().send_otp(phone=normalized, message=str(message))

    return {
        "phone": normalized,
        "expires_in": ttl,
        "resend_in": cooldown,
        "test_mode": bool(getattr(settings, "OTP_TEST", False)),
        "kind": kind,
    }


@transaction.atomic
def verify_otp(
    *,
    phone: str,
    code: str,
    kind: str = KIND_LOGIN,
    acting_user: BaseUser | None = None,
) -> BaseUser:
    """
    Validate OTP for ``kind``, then:

    - ``register`` → create the staged account (password stored hashed in pending)
    - ``profile_update`` → apply staged phone change (requires ``acting_user`` owner)
    - ``login`` → get-or-create user by phone
    """
    if kind not in {KIND_LOGIN, KIND_REGISTER, KIND_PROFILE_UPDATE}:
        raise ValidationError(
            _("Invalid verification challenge."),
            code=UserErrorCode.OTP_INVALID,
        )

    normalized = validate_phone(phone=phone)
    raw_code = (code or "").strip()
    key = _challenge_key(phone=normalized, kind=kind)

    payload = cache.get(key)
    if not payload:
        raise ValidationError(
            _("Verification code expired or not requested."),
            code=UserErrorCode.OTP_EXPIRED,
        )

    expires_at = float(payload.get("expires_at", 0))
    if expires_at and time.time() > expires_at:
        cache.delete(key)
        raise ValidationError(
            _("Verification code expired or not requested."),
            code=UserErrorCode.OTP_EXPIRED,
        )

    attempts = int(payload.get("attempts", 0))
    max_attempts = int(getattr(settings, "OTP_MAX_ATTEMPTS", 5))
    if attempts >= max_attempts:
        cache.delete(key)
        raise ValidationError(
            _("Too many invalid attempts. Request a new code."),
            code=UserErrorCode.OTP_TOO_MANY_ATTEMPTS,
        )

    if _hash_code(code=raw_code) != payload.get("code_hash"):
        payload["attempts"] = attempts + 1
        remaining = max(int(expires_at - time.time()), 1)
        cache.set(key, payload, timeout=remaining)
        raise ValidationError(
            _("Invalid verification code."),
            code=UserErrorCode.OTP_INVALID,
        )

    pending = payload.get("pending")
    pending_kind = (pending or {}).get("kind") or kind

    # Authorize profile updates before consuming the challenge.
    if pending_kind == KIND_PROFILE_UPDATE:
        _assert_profile_update_actor(
            user_id=(pending or {}).get("user_id"),
            acting_user=acting_user,
        )

    cache.delete(key)
    cache.delete(_cooldown_key(phone=normalized, kind=kind))

    if kind == KIND_LOGIN or not pending:
        return _get_or_create_user_by_phone(phone=normalized)

    if pending_kind == KIND_REGISTER:
        return _complete_pending_register(phone=normalized, data=pending.get("data") or {})
    if pending_kind == KIND_PROFILE_UPDATE:
        return _complete_pending_profile_update(
            phone=normalized,
            user_id=pending.get("user_id"),
            data=pending.get("data") or {},
            acting_user=acting_user,
        )

    raise ValidationError(
        _("Invalid verification challenge."),
        code=UserErrorCode.OTP_INVALID,
    )


def hash_register_password(*, password: str) -> str:
    """Hash a register password before storing it in the OTP pending payload."""
    return make_password(password)


def _complete_pending_register(*, phone: str, data: dict[str, Any]) -> BaseUser:
    existing = BaseUser.objects.filter(phone=phone).first()
    if existing is not None:
        if not existing.is_active:
            raise ValidationError(
                _("This account is inactive."),
                code=UserErrorCode.ACCOUNT_INACTIVE,
            )
        return existing

    password_hash = data.get("password_hash")
    if not password_hash:
        raise ValidationError(
            _("Invalid verification challenge."),
            code=UserErrorCode.OTP_INVALID,
        )

    try:
{%- if cookiecutter.user_login_field == "username" %}
        user = BaseUser.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=None,
            phone=phone,
        )
{%- else %}
        user = BaseUser.objects.create_user(
            email=data["email"],
            password=None,
            phone=phone,
        )
{%- endif %}
    except IntegrityError as error:
        map_integrity_error(error, model=BaseUser)
        raise

    user.password = password_hash
    model_save(instance=user, update_fields=["password"])

    if data.get("bio") is not None:
        profile = Profile.objects.get(user=user)
        profile.bio = data.get("bio")
        model_save(instance=profile, update_fields=["bio"])

    return user


def _assert_profile_update_actor(*, user_id: Any, acting_user: BaseUser | None) -> None:
    if user_id is None:
        raise ValidationError(
            _("Invalid verification challenge."),
            code=UserErrorCode.OTP_INVALID,
        )
    if acting_user is None or not getattr(acting_user, "is_authenticated", False):
        raise ValidationError(
            _("Authentication is required to confirm a profile phone change."),
            code=UserErrorCode.OTP_INVALID,
        )
    if str(acting_user.pk) != str(user_id):
        raise ValidationError(
            _("This verification code does not belong to the current user."),
            code=UserErrorCode.OTP_INVALID,
        )


def _complete_pending_profile_update(
    *,
    phone: str,
    user_id: Any,
    data: dict[str, Any],
    acting_user: BaseUser | None,
) -> BaseUser:
    from {{cookiecutter.project_slug}}.users.services.user_services import profile_update

    _assert_profile_update_actor(user_id=user_id, acting_user=acting_user)

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
    if "phone" in data:
        update_data["phone"] = data.get("phone")
        if update_data["phone"] is not None and update_data["phone"] != phone:
            raise ValidationError(
                _("Phone does not match the verification challenge."),
                code=UserErrorCode.OTP_INVALID,
            )

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
