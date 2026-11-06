from __future__ import annotations

from django.conf import settings

from {{cookiecutter.project_slug}}.users.providers.social.base import SocialIdentity, SocialProvider
{%- if cookiecutter.use_google_login == "y" %}
from {{cookiecutter.project_slug}}.users.providers.social.google import GoogleSocialProvider
{%- endif %}
{%- if cookiecutter.use_microsoft_login == "y" %}
from {{cookiecutter.project_slug}}.users.providers.social.microsoft import MicrosoftSocialProvider
{%- endif %}
{%- if cookiecutter.use_apple_login == "y" %}
from {{cookiecutter.project_slug}}.users.providers.social.apple import AppleSocialProvider
{%- endif %}

_REGISTRY: dict[str, type[SocialProvider]] = {}
{%- if cookiecutter.use_google_login == "y" %}
_REGISTRY["google"] = GoogleSocialProvider
{%- endif %}
{%- if cookiecutter.use_microsoft_login == "y" %}
_REGISTRY["microsoft"] = MicrosoftSocialProvider
{%- endif %}
{%- if cookiecutter.use_apple_login == "y" %}
_REGISTRY["apple"] = AppleSocialProvider
{%- endif %}


def get_social_provider(*, name: str) -> SocialProvider:
    """Factory — Strategy selection by provider name."""
    enabled = set(getattr(settings, "SOCIAL_AUTH_PROVIDERS", ()) or ())
    if name not in enabled:
        raise ValueError(f"Social provider {name!r} is not enabled")
    try:
        provider_cls = _REGISTRY[name]
    except KeyError as exc:
        known = ", ".join(sorted(_REGISTRY)) or "(none)"
        raise ValueError(f"Unknown social provider {name!r}. Known: {known}") from exc
    return provider_cls()


__all__ = ["SocialIdentity", "SocialProvider", "get_social_provider"]
