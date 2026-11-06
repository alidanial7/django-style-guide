from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import jwt
from jwt import PyJWKClient

from {{cookiecutter.project_slug}}.users.errors.codes import UserErrorCode
from {{cookiecutter.project_slug}}.users.providers.social.base import SocialIdentity, SocialProvider


class MicrosoftSocialProvider(SocialProvider):
    name = "microsoft"

    def verify_id_token(self, *, id_token: str) -> SocialIdentity:
        client_id = getattr(settings, "MICROSOFT_OAUTH_CLIENT_ID", "") or ""
        tenant = getattr(settings, "MICROSOFT_OAUTH_TENANT", "common") or "common"
        if not client_id:
            raise ValidationError(
                _("Microsoft login is not configured."),
                code=UserErrorCode.SOCIAL_NOT_CONFIGURED,
            )

        jwks_url = f"https://login.microsoftonline.com/{tenant}/discovery/v2.0/keys"
        issuer = f"https://login.microsoftonline.com/{tenant}/v2.0"

        try:
            jwks_client = PyJWKClient(jwks_url, cache_keys=True)
            signing_key = jwks_client.get_signing_key_from_jwt(id_token)
            claims = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=["RS256"],
                audience=client_id,
                options={"verify_iss": tenant != "common"},
            )
            if tenant == "common":
                token_iss = str(claims.get("iss") or "")
                if "login.microsoftonline.com" not in token_iss:
                    raise jwt.InvalidIssuerError("Unexpected Microsoft issuer")
            elif claims.get("iss") != issuer:
                raise jwt.InvalidIssuerError("Unexpected Microsoft issuer")
        except jwt.PyJWTError as exc:
            raise ValidationError(
                _("Invalid Microsoft id_token."),
                code=UserErrorCode.SOCIAL_TOKEN_INVALID,
            ) from exc

        email = (
            (claims.get("email") or claims.get("preferred_username") or "").strip().lower()
        )
        subject = str(claims.get("sub") or claims.get("oid") or "").strip()
        if not email or not subject:
            raise ValidationError(
                _("Microsoft token is missing email or subject."),
                code=UserErrorCode.SOCIAL_TOKEN_INVALID,
            )

        return SocialIdentity(
            provider=self.name,
            subject=subject,
            email=email,
            email_verified=True,
        )
