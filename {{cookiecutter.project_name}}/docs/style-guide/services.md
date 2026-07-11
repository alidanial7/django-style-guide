# ⚙️ Services

> **Writes** and **business rules** live here: create/update/delete, transactions, domain validation that is not just “field shape”, and integrity-error mapping.
>
> Views stay thin: parse input → call a service → return `api_response`.

---

## 🎯 Role

```mermaid
flowchart TB
    API[APIView] --> SER[InputSerializer]
    SER --> SVC[services/]
    SVC --> HELP["common.services model_*"]
    SVC --> MGR[manager / ORM]
    SVC --> SEL[selector — optional reads]
    HELP --> DB[(DB)]
    MGR --> DB
    SVC -->|ValidationError| ENV[api_exception_handler]
    API --> ENV2[api_response]
```

| Layer | Owns |
|-------|------|
| Serializer | Types, max_length, field validators, cross-field *input* checks |
| Service | Persist, workflows, domain failures with codes, integrity mapping |
| Selector | Reads the service needs before/after a write |

---

## 📂 Location & naming

```text
users/services/
├── __init__.py              # re-export public functions
├── user_services.py
└── tests/
    └── test_user_services.py
```

```python
# users/services/__init__.py
from .user_services import change_password, create_user, profile_update, register, ...

__all__ = ["change_password", "create_user", ...]
```

### Function style

- Verb-oriented names: `register`, `create_user`, `profile_update`, `change_password`, `logout`
- **Keyword-only** arguments after `*`
- Return model instances (or `None` when the contract is side-effect-only, e.g. password reset request)
- Raise Django `ValidationError` (field-keyed) for expected domain failures

```python
def register(
    *,
    email: str,
    password: str,
    bio: str | None = None,
    avatar=None,
) -> BaseUser:
    ...
```

---

## 🧱 Persistence helpers (`common.services`)

Prefer these for ordinary model writes. They:

1. wrap work in `transaction.atomic()`  
2. call `full_clean()`  
3. catch `IntegrityError` and call `map_integrity_error`  

| Helper | Signature (conceptually) | Use when |
|--------|--------------------------|----------|
| `model_create` | `(*, model_class, data: dict) -> instance` | Creating from a field dict |
| `model_save` | `(*, instance, update_fields=None) -> instance` | Saving an instance you already mutated |
| `model_update` | `(*, instance, fields, data) -> (instance, has_updated)` | Patch only listed fields if values changed |

```python
from {{cookiecutter.project_slug}}.common.services import model_create, model_save, model_update

post = model_create(model_class=Post, data={"title": title, "author": author})

model_save(instance=profile, update_fields=["bio", "avatar"])

profile, changed = model_update(
    instance=profile,
    fields=["bio", "avatar"],
    data={"bio": bio, "avatar": avatar},
)
```

### When you bypass `model_*` (managers, `set_password`, …)

Some paths cannot use `model_create` (e.g. `BaseUser.objects.create_user` hashes passwords). Then **you** must map integrity errors:

```python
from django.db import IntegrityError

from {{cookiecutter.project_slug}}.common.db.integrity import map_integrity_error


def create_user(*, email: str, password: str) -> BaseUser:
    try:
        return BaseUser.objects.create_user(email=email, password=password)
    except IntegrityError as error:
        map_integrity_error(error, model=BaseUser)
        raise  # map_integrity_error never returns; keeps type-checkers happy
```

```mermaid
sequenceDiagram
    participant S as create_user service
    participant M as BaseUserManager
    participant DB as PostgreSQL
    participant MAP as map_integrity_error

    S->>M: create_user(email, password)
    M->>DB: INSERT
    alt duplicate email
        DB-->>M: IntegrityError
        M-->>S: IntegrityError
        S->>MAP: map_integrity_error(...)
        MAP-->>S: ValidationError messages.email code=unique
    else ok
        DB-->>M: row
        M-->>S: BaseUser
    end
```

**Rule:** every persistence path uses `model_create` / `model_save` / `model_update` **or** explicit `except IntegrityError: map_integrity_error(...); raise`. No bare `objects.create()` in services without mapping.

---

## 🔁 Transactions

Multi-step writes need atomicity so you don’t leave half-created state.

```python
@transaction.atomic
def register(*, email: str, password: str, bio: str | None = None, avatar=None) -> BaseUser:
    user = create_user(email=email, password=password)
    profile = Profile.objects.get(user=user)  # created by signal

    update_fields: list[str] = []
    if bio:
        profile.bio = bio
        update_fields.append("bio")
    if avatar is not None:
        profile.avatar = avatar
        update_fields.append("avatar")

    if update_fields:
        model_save(instance=profile, update_fields=update_fields)

    return user
```

| Tool | When |
|------|------|
| `@transaction.atomic` on the service | Several ORM operations that must succeed/fail together |
| Atomic block inside `model_*` | Single-instance create/save already covered |
| Nested atomics | OK — Django uses savepoints; don’t over-nest without reason |

---

## 🚨 Raising domain errors from services

Raise Django’s `ValidationError` (not DRF’s) with **field keys** and **codes**. The [API exception handler](api-envelope.md) normalizes them into `messages`.

```python
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from {{cookiecutter.project_slug}}.users.errors.codes import UserErrorCode


def change_password(*, user: BaseUser, current_password: str, new_password: str) -> None:
    if not user.check_password(current_password):
        raise ValidationError(
            {
                "current_password": ValidationError(
                    _("current password is incorrect."),
                    code=UserErrorCode.PASSWORD_INCORRECT,
                )
            }
        )
    user.set_password(new_password)
    user.save(update_fields=["password"])
```

| ✅ Do | ❌ Don’t |
|-------|---------|
| Field-keyed dict errors | Bare string-only errors when a field is known |
| Domain `UserErrorCode` / app codes | Random undocumented string codes |
| Lowercase gettext messages | Hard-coded untranslated UI strings (see [Translations](translations.md)) |
| Let unexpected bugs propagate / log | Swallow `IntegrityError` without mapping |

Other real services in this repo:

| Function | Behavior |
|----------|----------|
| `profile_update` | Patches bio/avatar via `model_save` |
{%- if cookiecutter.use_jwt == "y" %}
| `logout` | Blacklists refresh token; invalid token → `UserErrorCode.INVALID_TOKEN` |
{%- endif %}
| `request_password_reset` | Always succeeds; emails only if user exists (no email enumeration) |
| `reset_password` | Validates uid/token; sets password |

---

## 🆚 Service vs serializer vs selector vs signal

| Concern | Put it in |
|---------|-----------|
| `EmailField`, `max_length`, `PASSWORD_VALIDATORS` | Input serializer |
| `confirm_password` must match | Input serializer `validate()` |
| Unique email enforcement | DB `unique=True` + service integrity mapping |
| “Current password is wrong” | Service |
| “Fetch profile before patch” | Selector called by API/service |
| “Ensure Profile row exists on user create” | Signal (mechanical) + service for updates |

```python
# ❌ uniqueness check only in serializer
if BaseUser.objects.filter(email=email).exists():
    raise ValidationError(...)

# ✅ DB unique + create_user → map_integrity_error
```

---

## 📞 How APIs call services

```python
# users/apis/users/register/users_register_apis.py
def post(self, request):
    serializer = UsersRegisterInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = register(
        email=serializer.validated_data.get("email"),
        password=serializer.validated_data.get("password"),
        bio=serializer.validated_data.get("bio"),
        avatar=serializer.validated_data.get("avatar"),
    )
    return api_response(
        data=UsersRegisterOutputSerializer(user, context={"request": request}).data,
        http_status=status.HTTP_201_CREATED,
    )
```

```python
# users/apis/users/profile/users_profile_apis.py
def patch(self, request):
    serializer = UsersProfileUpdateInputSerializer(data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    profile = get_profile(user=request.user)  # selector
    profile = profile_update(                 # service
        profile=profile,
        bio=serializer.validated_data.get("bio"),
        avatar=serializer.validated_data.get("avatar"),
    )
    return api_response(data=UsersProfileOutputSerializer(profile, context={"request": request}).data)
```

**APIs never call `Model.objects.create` / `.save()` directly for product writes.**

---

## 🧪 Testing

Tests live under `services/tests/`.

| Cover | Example |
|-------|---------|
| Happy path | `register` returns user with profile fields |
| Domain validation | `change_password` with wrong current password |
| Integrity | Duplicate email → error with `unique` (or mapped field) |
| Side-effect contracts | `request_password_reset` does not leak whether email exists |

Use factories from `users/tests/user_factories.py` (or app factories from `start_domain_app`) instead of hand-building invalid graphs when possible.

---

## ✅ Checklist: adding a service

1. Add `def feature(*, ...) -> ...` in `<app>/services/<domain>_services.py`  
2. Use `model_*` or `map_integrity_error` on every write  
3. Wrap multi-step work in `@transaction.atomic`  
4. Raise field-keyed `ValidationError` with domain codes  
5. Re-export from `services/__init__.py`  
6. Call only from APIs / management commands / admin hooks — not from serializers  
7. Add `services/tests/…`  

### ❌ Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| Fat `APIView.post` with ORM writes | Move to service |
| `objects.create()` without integrity mapping | `model_create` or `map_integrity_error` |
| Business rules only in serializer | Service + DB constraints |
| Service returns `Response` | Return models; API builds envelope |
| Silent `except IntegrityError: pass` | Always map or re-raise |
| Mixing huge read/report queries into write services | Call a selector instead |

---

## 🔗 Related docs

| Doc | Why |
|-----|-----|
| [Selectors](selectors.md) | Reads used before/after writes |
| [Models](models.md) | Constraints the service relies on |
| [Validation & errors](validation-and-errors.md) | Codes + integrity details |
| [API envelope](api-envelope.md) | How service errors become JSON |
| [APIs](apis.md) | Thin callers |
| [Signals](signals.md) | Mechanical creates vs service updates |
