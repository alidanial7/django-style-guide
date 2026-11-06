from enum import StrEnum


class UserErrorCode(StrEnum):
    """Users-domain machine codes (identity / auth / password)."""

    PASSWORD_MISSING_NUMBER = "password_must_include_number"
    PASSWORD_MISSING_LETTER = "password_must_include_letter"
    PASSWORD_MISSING_SPECIAL = "password_must_include_special_char"
    PASSWORD_MISMATCH = "password_mismatch"
    PASSWORD_TOO_SHORT = "password_too_short"
    PASSWORD_INCORRECT = "password_incorrect"
    INVALID_RESET_TOKEN = "invalid_reset_token"
    INVALID_TOKEN = "invalid_token"
{%- if cookiecutter.use_otp_login == "y" or cookiecutter.use_google_login == "y" or cookiecutter.use_microsoft_login == "y" or cookiecutter.use_apple_login == "y" %}
    ACCOUNT_INACTIVE = "account_inactive"
{%- endif %}
{%- if cookiecutter.use_otp_login == "y" %}
    INVALID_PHONE = "invalid_phone"
    OTP_INVALID = "otp_invalid"
    OTP_EXPIRED = "otp_expired"
    OTP_TOO_MANY_ATTEMPTS = "otp_too_many_attempts"
    OTP_RESEND_COOLDOWN = "otp_resend_cooldown"
{%- endif %}
{%- if cookiecutter.use_google_login == "y" or cookiecutter.use_microsoft_login == "y" or cookiecutter.use_apple_login == "y" %}
    SOCIAL_NOT_CONFIGURED = "social_not_configured"
    SOCIAL_TOKEN_INVALID = "social_token_invalid"
    SOCIAL_EMAIL_REQUIRED = "social_email_required"
    SOCIAL_EMAIL_UNVERIFIED = "social_email_unverified"
{%- endif %}
