# Services

Services own **writes** and **business rules**. Views call services; services call the ORM (or `common.services` helpers) and raise Django `ValidationError` / domain errors when rules fail.

## Location & naming

```text
<app>/services/
├── __init__.py              # re-export public functions
└── <domain>_services.py     # e.g. user_services.py
```

Prefer keyword-only arguments:

```python
def register(*, email: str, password: str, bio: str | None = None, avatar=None) -> BaseUser:
    ...
```

## Persistence helpers (`common.services`)

Prefer these for ordinary model writes — they run `full_clean()`, wrap in `transaction.atomic()`, and map `IntegrityError`:

| Helper | Use |
|--------|-----|
| `model_create(model_class=..., data=...)` | Create from a dict |
| `model_save(instance=..., update_fields=...)` | Save existing instance |
| `model_update(instance=..., fields=..., data=...)` | Patch listed fields; returns `(instance, has_updated)` |

When a manager method bypasses these helpers (e.g. `BaseUser.objects.create_user`), catch integrity errors yourself:

```python
from django.db import IntegrityError
from {{cookiecutter.project_slug}}.common.db.integrity import map_integrity_error

try:
    return BaseUser.objects.create_user(email=email, password=password)
except IntegrityError as error:
    map_integrity_error(error, model=BaseUser)
    raise
```

`map_integrity_error` **never returns** — it raises a field-keyed `ValidationError` (or controlled API exception). The trailing `raise` keeps type-checkers happy.

## Transactions

Use `@transaction.atomic` (or the atomic block inside `model_*`) for multi-step writes. Example: `register` creates the user, then updates the related profile.

## Raising validation errors from services

Raise Django’s `ValidationError` with field keys and domain codes — the API exception handler normalizes them into the envelope:

```python
raise ValidationError(
    {
        "current_password": ValidationError(
            _("current password is incorrect."),
            code=UserErrorCode.PASSWORD_INCORRECT,
        )
    }
)
```

## What belongs in a service vs serializer

| Belongs in service | Belongs in serializer |
|--------------------|------------------------|
| Persist user / profile | Field types, max_length |
| Password change / reset logic | `validators=PASSWORD_VALIDATORS` |
| Token blacklist on logout | Confirm-password cross-field check |
| Integrity mapping | Input-only shape |

## Tests

Service tests live under `services/tests/`. Cover happy paths, validation failures, and integrity/unique cases where practical.
