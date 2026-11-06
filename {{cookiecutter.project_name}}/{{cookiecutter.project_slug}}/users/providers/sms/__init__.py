from __future__ import annotations

from django.conf import settings

from {{cookiecutter.project_slug}}.users.providers.sms.base import SmsProvider
from {{cookiecutter.project_slug}}.users.providers.sms.stub import StubSmsProvider

# Registry: add new providers here and select via SMS_PROVIDER env.
_SMS_PROVIDERS: dict[str, type[SmsProvider]] = {
    "stub": StubSmsProvider,
}


def get_sms_provider() -> SmsProvider:
    """Factory — Strategy selection from ``settings.SMS_PROVIDER``."""
    key = getattr(settings, "SMS_PROVIDER", "stub")
    try:
        provider_cls = _SMS_PROVIDERS[key]
    except KeyError as exc:
        known = ", ".join(sorted(_SMS_PROVIDERS))
        raise ValueError(f"Unknown SMS_PROVIDER={key!r}. Known: {known}") from exc
    return provider_cls()


__all__ = ["SmsProvider", "StubSmsProvider", "get_sms_provider"]
