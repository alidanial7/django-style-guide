# Signals & constants

## Constants

Put app-level constants in `<app>/constants.py`:

- OpenAPI / Swagger tags
- Static asset paths
- Magic strings shared across apis/services

Example from `users`:

```python
USERS_TAGS = ["users"]
AUTH_TAGS = ["auth"]
DEFAULT_AVATAR_STATIC_PATH = "users/default_avatar.png"
```

Avoid scattering string literals for the same concept across modules.

## Signals

Signals live under `<app>/signals/` and are imported from the app config `ready()` when needed.

Guidelines:

- Prefer **explicit service calls** over signals for business workflows.
- Use signals for mechanical side effects (e.g. create a `Profile` when a `BaseUser` is created).
- Keep signal handlers idempotent; absorb races (`get_or_create`, catch `IntegrityError`).
- Do not treat signals as an API boundary — they should not raise user-facing validation for HTTP clients.

Example pattern (`users/signals/user_signals.py`): on `BaseUser` post_save create, ensure a `Profile` exists.
