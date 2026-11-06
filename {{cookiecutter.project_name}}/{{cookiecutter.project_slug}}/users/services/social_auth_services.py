from __future__ import annotations

import secrets

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils.translation import gettext_lazy as _

from {{cookiecutter.project_slug}}.common.db.integrity import map_integrity_error
from {{cookiecutter.project_slug}}.users.errors.codes import UserErrorCode
from {{cookiecutter.project_slug}}.users.models import BaseUser, SocialAccount
from {{cookiecutter.project_slug}}.users.providers.social import get_social_provider
from {{cookiecutter.project_slug}}.users.providers.social.base import SocialIdentity


@transaction.atomic
def social_login(*, provider: str, id_token: str) -> BaseUser:
    """
    Verify provider ``id_token``, link/create local user, return the user.

    After this, callers issue JWT or establish a session (same as password/OTP).
    """
    identity = get_social_provider(name=provider).verify_id_token(id_token=id_token)
    return _resolve_user_from_identity(identity=identity)


def _resolve_user_from_identity(*, identity: SocialIdentity) -> BaseUser:
    existing_link = (
        SocialAccount.objects.select_related("user")
        .filter(provider=identity["provider"], subject=identity["subject"])
        .first()
    )
    if existing_link is not None:
        user = existing_link.user
        if not user.is_active:
            raise ValidationError(
                _("This account is inactive."),
                code=UserErrorCode.ACCOUNT_INACTIVE,
            )
        return user

    email = identity["email"].strip().lower()
    if not email:
        raise ValidationError(
            _("Provider did not return an email; cannot create an account."),
            code=UserErrorCode.SOCIAL_EMAIL_REQUIRED,
        )
    if not identity["email_verified"]:
        raise ValidationError(
            _("Provider email is not verified."),
            code=UserErrorCode.SOCIAL_EMAIL_UNVERIFIED,
        )

    user = BaseUser.objects.filter(email=email).first()
    if user is None:
        user = _create_user_for_social(email=email)
    elif not user.is_active:
        raise ValidationError(
            _("This account is inactive."),
            code=UserErrorCode.ACCOUNT_INACTIVE,
        )

    try:
        SocialAccount.objects.create(
            user=user,
            provider=identity["provider"],
            subject=identity["subject"],
        )
    except IntegrityError as error:
        map_integrity_error(error, model=SocialAccount)
        raise

    return user


def _create_user_for_social(*, email: str) -> BaseUser:
    try:
{%- if cookiecutter.user_login_field == "username" %}
        base = email.split("@", 1)[0][:120] or "user"
        username = base
        for _ in range(8):
            if not BaseUser.objects.filter(username=username).exists():
                break
            username = f"{base}_{secrets.token_hex(2)}"
        return BaseUser.objects.create_user(
            username=username,
            email=email,
            password=None,
        )
{%- else %}
        return BaseUser.objects.create_user(email=email, password=None)
{%- endif %}
    except IntegrityError as error:
        map_integrity_error(error, model=BaseUser)
        raise
