from django.conf import settings
from django.urls import reverse


def api_reverse(name: str, *args, scope: str | None = None, **kwargs) -> str:
    """
    Reverse an API route.

    ``name`` is ``users:register`` / ``auth:login`` (no ``api:`` prefix).
    When multi-scope is enabled, prefixes ``scope`` or the first configured
    scope (``api:<scope>:users:register``).
    """
    scopes = getattr(settings, "API_SCOPES", None) or ()
    if scopes:
        chosen = scope or scopes[0]
        return reverse(f"api:{chosen}:{name}", *args, **kwargs)
    return reverse(f"api:{name}", *args, **kwargs)
