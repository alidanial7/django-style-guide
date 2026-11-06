from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import jwt
from jwt import PyJWKClient

from {{cookiecutter.project_slug}}.users.errors.codes import UserErrorCode
from {{cookiecutter.project_slug}}.users.providers.social.base import SocialIdentity, SocialProvider

_APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"
_APPLE_ISSUER = "https://appleid.apple.com"


class AppleSocialProvider(SocialProvider):
    name = "apple"

    def verify_id_token(self, *, id_token: str) -> SocialIdentity:
        client_id = getattr(settings, "APPLE_OAUTH_CLIENT_ID", "") or ""
        if not client_id:
            raise ValidationError(
                _("Apple login is not configured."),
                code=UserErrorCode.SOCIAL_NOT_CONFIGURED,
            )

        try:
            jwks_client = PyJWKClient(_APPLE_JWKS_URL, cache_keys=True)
            signing_key = jwks_client.get_signing_key_from_jwt(id_token)
            claims = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=["RS256"],
                audience=client_id,
                issuer=_APPLE_ISSUER,
            )
        except jwt.PyJWTError as exc:
            raise ValidationError(
                _("Invalid Apple id_token."),
                code=UserErrorCode.SOCIAL_TOKEN_INVALID,
            ) from exc

        subject = str(claims.get("sub") or "").strip()
        email = (claims.get("email") or "").strip().lower()
        # Apple may omit email on subsequent logins — caller must already have SocialAccount.
        if not subject:
            raise ValidationError(
                _("Apple token is missing subject."),
                code=UserErrorCode.SOCIAL_TOKEN_INVALID,
            )

        return SocialIdentity(
            provider=self.name,
            subject=subject,
            email=email,
            email_verified=bool(claims.get("email_verified", True)),
        )
