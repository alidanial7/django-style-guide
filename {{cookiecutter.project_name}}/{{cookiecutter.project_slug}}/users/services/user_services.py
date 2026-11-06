from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError
{%- if cookiecutter.use_file_manager == "y" %}
from django.core.files.uploadedfile import UploadedFile
{%- endif %}
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
{%- if cookiecutter.use_jwt == "y" %}
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
{%- endif %}

from {{cookiecutter.project_slug}}.common.db.integrity import map_integrity_error
from {{cookiecutter.project_slug}}.common.services import model_save, model_update
{%- if cookiecutter.use_file_manager == "y" %}
from {{cookiecutter.project_slug}}.file_manager.services.file_services import create_managed_file
{%- endif %}
from {{cookiecutter.project_slug}}.users.errors.codes import UserErrorCode
from {{cookiecutter.project_slug}}.users.models import BaseUser, Profile
from {{cookiecutter.project_slug}}.users.types import ChangePasswordData, ProfileUpdateData, RegisterData

_password_reset_token_generator = PasswordResetTokenGenerator()


{%- if cookiecutter.user_login_field == "username" %}
def create_user(
    *,
    username: str,
    email: str,
    password: str,
{%- if cookiecutter.use_otp_login == "y" %}
    phone: str | None = None,
{%- endif %}
) -> BaseUser:
    try:
        return BaseUser.objects.create_user(
            username=username,
            email=email,
            password=password,
{%- if cookiecutter.use_otp_login == "y" %}
            phone=phone,
{%- endif %}
        )
    except IntegrityError as error:
        map_integrity_error(error, model=BaseUser)
        raise  # map_integrity_error never returns; keep type-checkers happy
{%- else %}
def create_user(
    *,
    email: str,
    password: str,
{%- if cookiecutter.use_otp_login == "y" %}
    phone: str | None = None,
{%- endif %}
) -> BaseUser:
    try:
        return BaseUser.objects.create_user(
            email=email,
            password=password,
{%- if cookiecutter.use_otp_login == "y" %}
            phone=phone,
{%- endif %}
        )
    except IntegrityError as error:
        map_integrity_error(error, model=BaseUser)
        raise  # map_integrity_error never returns; keep type-checkers happy
{%- endif %}

{% if cookiecutter.use_file_manager == "y" %}

def _resolve_avatar(*, user: BaseUser, avatar: UploadedFile | None):
    if avatar is None:
        return None
    return create_managed_file(
        user=user,
        file_obj=avatar,
        title=f"{user.email} avatar",
        category="avatar",
        is_public=True,
    )

{% endif %}

@transaction.atomic
def register(*, data: RegisterData) -> BaseUser:
{%- if cookiecutter.user_login_field == "username" %}
    user = create_user(
        username=data["username"],
        email=data["email"],
        password=data["password"],
{%- if cookiecutter.use_otp_login == "y" %}
        phone=data.get("phone"),
{%- endif %}
    )
{%- else %}
    user = create_user(
        email=data["email"],
        password=data["password"],
{%- if cookiecutter.use_otp_login == "y" %}
        phone=data.get("phone"),
{%- endif %}
    )
{%- endif %}
    profile = Profile.objects.get(user=user)

    update_fields: list[str] = []
    if data.get("bio"):
        profile.bio = data["bio"]
        update_fields.append("bio")
    if data.get("avatar") is not None:
{%- if cookiecutter.use_file_manager == "y" %}
        profile.avatar = _resolve_avatar(user=user, avatar=data["avatar"])
{%- else %}
        profile.avatar = data["avatar"]
{%- endif %}
        update_fields.append("avatar")

    if update_fields:
        model_save(instance=profile, update_fields=update_fields)

    return user


def profile_update(*, profile: Profile, data: ProfileUpdateData) -> Profile:
    """Apply only keys present in ``data`` — PATCH-safe; ``None`` ≠ missing."""
    payload = dict(data)
{%- if cookiecutter.use_otp_login == "y" %}
    phone_provided = "phone" in payload
    phone_value = payload.pop("phone", None) if phone_provided else None
{%- endif %}
{%- if cookiecutter.use_file_manager == "y" %}
    if "avatar" in payload and isinstance(payload["avatar"], UploadedFile):
        payload["avatar"] = _resolve_avatar(user=profile.user, avatar=payload["avatar"])
{%- endif %}
    profile, _changed = model_update(
        instance=profile,
        fields=["bio", "avatar"],
        data=payload,
    )
{%- if cookiecutter.use_otp_login == "y" %}
    if phone_provided:
        user = profile.user
        user.phone = phone_value
        try:
            model_save(instance=user, update_fields=["phone"])
        except IntegrityError as error:
            map_integrity_error(error, model=BaseUser)
            raise
{%- endif %}
    return profile


def change_password(*, user: BaseUser, data: ChangePasswordData) -> None:
    if not user.check_password(data["current_password"]):
        raise ValidationError(
            {
                "current_password": ValidationError(
                    _("current password is incorrect."),
                    code=UserErrorCode.PASSWORD_INCORRECT,
                )
            }
        )
    user.set_password(data["new_password"])
    user.save(update_fields=["password"])

{% if cookiecutter.use_jwt == "y" %}
def logout(*, refresh_token: str) -> None:
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError as error:
        raise ValidationError(
            {
                "refresh": ValidationError(
                    _("token is invalid or expired."),
                    code=UserErrorCode.INVALID_TOKEN,
                )
            }
        ) from error

{% endif %}
def request_password_reset(*, email: str) -> None:
    """Always succeeds. Sends a reset email only when the account exists."""
    try:
        user = BaseUser.objects.get(email__iexact=email.strip().lower())
    except BaseUser.DoesNotExist:
        return

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = _password_reset_token_generator.make_token(user)
    app_domain = getattr(settings, "APP_DOMAIN", "http://localhost:8000").rstrip("/")
    reset_path = f"{app_domain}/reset-password?uid={uid}&token={token}"

    send_mail(
        subject=_("password reset"),
        message=(
            f"{_('use the following details to reset your password:')}\n\n"
            f"uid: {uid}\n"
            f"token: {token}\n"
            f"link: {reset_path}\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


def reset_password(*, uidb64: str, token: str, new_password: str) -> BaseUser:
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = BaseUser.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, BaseUser.DoesNotExist) as error:
        raise ValidationError(
            {
                "uid": ValidationError(
                    _("invalid password reset link."),
                    code=UserErrorCode.INVALID_RESET_TOKEN,
                )
            }
        ) from error

    if not _password_reset_token_generator.check_token(user, token):
        raise ValidationError(
            {
                "token": ValidationError(
                    _("invalid or expired password reset token."),
                    code=UserErrorCode.INVALID_RESET_TOKEN,
                )
            }
        )

    user.set_password(new_password)
    user.save(update_fields=["password"])
    return user
