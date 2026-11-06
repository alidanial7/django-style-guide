from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import jwt
from jwt import PyJWKClient

from {{cookiecutter.project_slug}}.users.errors.codes import UserErrorCode
from {{cookiecutter.project_slug}}.users.providers.social.base import SocialIdentity, SocialProvider

_GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
_GOOGLE_ISSUERS = ("https://accounts.google.com", "accounts.google.com")


class GoogleSocialProvider(SocialProvider):
    name = "google"

    def verify_id_token(self, *, id_token: str) -> SocialIdentity:
        client_id = getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", "") or ""
        if not client_id:
            raise ValidationError(
                _("Google login is not configured."),
                code=UserErrorCode.SOCIAL_NOT_CONFIGURED,
            )

        try:
            jwks_client = PyJWKClient(_GOOGLE_JWKS_URL, cache_keys=True)
            signing_key = jwks_client.get_signing_key_from_jwt(id_token)
            claims = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=["RS256"],
                audience=client_id,
                issuer=_GOOGLE_ISSUERS,
            )
        except jwt.PyJWTError as exc:
            raise ValidationError(
                _("Invalid Google id_token."),
                code=UserErrorCode.SOCIAL_TOKEN_INVALID,
            ) from exc

        email = (claims.get("email") or "").strip().lower()
        subject = str(claims.get("sub") or "").strip()
        if not email or not subject:
            raise ValidationError(
                _("Google token is missing email or subject."),
                code=UserErrorCode.SOCIAL_TOKEN_INVALID,
            )

        return SocialIdentity(
            provider=self.name,
            subject=subject,
            email=email,
            email_verified=bool(claims.get("email_verified", False)),
        )
