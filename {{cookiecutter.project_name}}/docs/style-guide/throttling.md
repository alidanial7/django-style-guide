# Throttling

Auth and registration endpoints use DRF `ScopedRateThrottle`.

## Configured rates

From `config/settings/drf.py` → `DEFAULT_THROTTLE_RATES`:

| Scope | Default rate | Typical endpoints |
|-------|--------------|-------------------|
| `auth` | `20/minute` | login, refresh, verify |
| `register` | `10/minute` | user registration |
| `password_reset` | `5/minute` | password reset request |

## Wiring a view

```python
from rest_framework.throttling import ScopedRateThrottle

class UsersRegisterApi(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"
```

## Production note

Prefer Redis (`use_redis=y` at generation, or enable later) in multi-worker production so throttle counters are shared across processes. In-memory throttling is per-process only.

## Adding a new scope

1. Add a key under `DEFAULT_THROTTLE_RATES` in `config/settings/drf.py`.
2. Set `throttle_classes` + `throttle_scope` on the view.
3. Document the limit in the endpoint’s style-guide / Swagger description if it matters to clients.
