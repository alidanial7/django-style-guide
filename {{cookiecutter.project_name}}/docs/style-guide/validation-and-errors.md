# Validation & errors

`common` = platform only. Each domain app (e.g. `users`) owns its identity/business codes and validators.

## Boundaries

| Layer | Location | Responsibility |
|-------|----------|----------------|
| Pure checks | `common/validators/` or `<app>/validators/` | `is_*` → `bool` only (no messages, no exceptions) |
| Platform codes | `common/errors/codes.py` → `ErrorCode` | Shared machine codes (`required`, `unique`, `not_null`, …) |
| Domain codes | `<app>/errors/codes.py` → e.g. `UserErrorCode` | App-specific codes. Codes only — never validators |
| Raising validators | `<app>/validators/` | `@deconstructible` classes that raise Django `ValidationError` with `code=` |
| Serializers | `<app>/apis/...` | Input shape + cross-field `validate()` only |
| Services / writes | `<app>/services/` + `common/services.py` | Business rules + persistence; always map integrity errors |
| Integrity mapping | `common/db/integrity/` | `IntegrityError` → field-keyed Django `ValidationError` / controlled `APIException` |
| API envelope | `common/http/` | See [API response envelope](api-envelope.md) |

**Do not** put domain password rules in `common`, raising validators in `errors/`, or business/permission rules in serializers/views.

## Messages

- Use `gettext_lazy` / `_()` with **lowercase** msgids.
- Parameterized `ValidationError` messages use `params={...}` — do not pre-format with `%`.

## 1. Platform error codes (`common`)

```python
# common/errors/codes.py
class ErrorCode(StrEnum):
    INVALID_FORMAT = "invalid_format"
    INVALID = "invalid"                # fallback when raiser omitted code=
    REQUIRED = "required"
    NOT_NULL = "not_null"              # DB NOT NULL / pgcode 23502
    UNIQUE = "unique"                  # unique / pgcode 23505
    INVALID_REFERENCE = "invalid_reference"  # FK / pgcode 23503
    UNKNOWN_INTEGRITY = "integrity_error"
    APPLICATION_ERROR = "application_error"
    SERVER_ERROR = "server_error"
```

`REQUIRED` = missing API/serializer input. `NOT_NULL` = database null violation. Keep them distinct.

## 2. Domain error codes (per app)

```python
# users/errors/codes.py
class UserErrorCode(StrEnum):
    PASSWORD_MISSING_NUMBER = "password_must_include_number"
    PASSWORD_MISSING_LETTER = "password_must_include_letter"
    PASSWORD_MISSING_SPECIAL = "password_must_include_special_char"
    PASSWORD_MISMATCH = "password_mismatch"
    PASSWORD_TOO_SHORT = "password_too_short"
    PASSWORD_INCORRECT = "password_incorrect"
    INVALID_RESET_TOKEN = "invalid_reset_token"
    INVALID_TOKEN = "invalid_token"
```

Add new apps the same way: `<app>/errors/codes.py` with an app-prefixed enum (`OrdersErrorCode`). Never reuse the platform name `ErrorCode` for domain codes.

## 3. Pure validators (`is_*`)

**Generic (any app):** helpers under `common/validators/` (see the commented `is_slug` example in `common/validators/string.py`).

```python
def is_slug(value: str) -> bool:
    return isinstance(value, str) and _SLUG_RE.fullmatch(value) is not None
```

**Domain:** pure checks live next to raising validators (e.g. top of `users/validators/password.py`):

```python
def is_password_with_number(value: str) -> bool:
    ...
```

Naming separates concerns: `is_*` (bool) vs `*Validator` (raises).

Rules: return `bool` only; no `ValidationError`, no `gettext`, no user-facing messages.

## 4. Raising field validators (`*Validator`)

Use Django’s `ValidationError` (not DRF’s) so the same class works on models and serializers:

```python
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

@deconstructible
class PasswordNumberValidator:
    code = UserErrorCode.PASSWORD_MISSING_NUMBER
    message = _("password must include number")

    def __call__(self, value: str) -> None:
        if not is_password_with_number(value):
            raise ValidationError(self.message, code=self.code)


@deconstructible
class PasswordMinLengthValidator:
    code = UserErrorCode.PASSWORD_TOO_SHORT
    message = _("password must be at least %(limit_value)d characters")
    limit_value = 10

    def __call__(self, value: str) -> None:
        if not isinstance(value, str) or len(value) < self.limit_value:
            raise ValidationError(
                self.message,
                code=self.code,
                params={"limit_value": self.limit_value},
            )
```

Export a list for DRF fields:

```python
PASSWORD_VALIDATORS = [
    validate_password_number,
    validate_password_letter,
    validate_password_special_char,
    validate_password_min_length,
]

password = serializers.CharField(validators=PASSWORD_VALIDATORS)
```

### Password policy (API + Django auth)

| Path | Setting / list | Used for |
|------|----------------|----------|
| API input | `users.validators.PASSWORD_VALIDATORS` | Register / DRF fields |
| Django auth | `AUTH_PASSWORD_VALIDATORS` in `config/settings/auth.py` | Admin / `set_password` (`Password*DjangoValidator` adapters + Django built-ins) |

Keep both in sync when changing password policy.

## 5. Serializers (shape + object rules only)

- Field validators: reuse domain `*Validator` lists.
- Cross-field rules: `validate()` with field-keyed errors.
- Uniqueness stays in the DB — see integrity below.

## 6. Services and integrity mapping

Every persistence path must either:

1. go through `common.services.model_create` / `model_save` / `model_update`, or
2. catch `IntegrityError` and call `map_integrity_error` (raise-only):

```python
from django.db import IntegrityError
from {{cookiecutter.project_slug}}.common.db.integrity import map_integrity_error
from {{cookiecutter.project_slug}}.common.services import model_create

instance = model_create(model_class=MyModel, data={...})

try:
    return MyModel.objects.create(...)
except IntegrityError as error:
    map_integrity_error(error, model=MyModel)
    raise
```

`common/db/integrity/` prefers Postgres `pgcode` (`23505` unique, `23502` not null, `23503` FK) with SQLite message fallback. Known columns become **field-keyed** errors in `messages`.

## 7. Checklist: add a new field rule

1. **Pure check** — generic → `common/validators/`; domain → `<app>/validators/` as `is_*`.
2. **Code** — platform → `ErrorCode`; domain → `<app>/errors/codes.py`.
3. **Raising validator** — `@deconstructible` in `<app>/validators/`, Django `ValidationError` + `code=`.
4. **Wire it** — model field when universal; serializer field for API input; cross-field only in `validate()`.
5. **Persist safely** — DB constraint for uniqueness/FK/null; writes via `model_*` or `map_integrity_error`.

## Example layout

```text
common/
  validators/string.py     # commented generic is_* example
  errors/codes.py          # ErrorCode (platform only)
  db/integrity/            # parse.py + map.py → map_integrity_error
  http/exception_handler.py
  services.py              # model_create / model_save wrap IntegrityError

users/
  errors/codes.py          # UserErrorCode only
  validators/password.py   # is_password_* + Password*Validator + PASSWORD_VALIDATORS
  services/                # create_user / register map integrity
  apis/.../register/       # serializers use PASSWORD_VALIDATORS + UserErrorCode
```

## `ApplicationError`

`core.exceptions.ApplicationError` is for controlled non-field application failures. The exception handler maps it to `ErrorCode.APPLICATION_ERROR` with optional `extra` field messages. Prefer domain `ValidationError` for field-level problems.
