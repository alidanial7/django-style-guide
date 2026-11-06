# Models

Domain data shape: package layout, `BaseModel`, DB constraints, managers, admin, migrations. Models do **not** own HTTP or workflows — use [selectors](selectors.md) / [services](services.md).

---

## Rules

### Package layout (one module per model)

```text
users/models/
├── __init__.py       # public exports
├── base_user.py
└── profile.py
```

```python
# users/models/__init__.py
from .base_user import BaseUser
from .profile import Profile

__all__ = ["BaseUser", "Profile"]
```

Import from the package root (`from {{cookiecutter.project_slug}}.users.models import BaseUser`). Never deep-import module files from APIs/services. File = snake_case of the class (`BlogPost` → `blog_post.py`). One primary model per file. Field choice enums live in [`enums.py`](enums.md) — **never** nested on the model.

### Labels, help text, Meta, docstrings

On **every** declared field: `verbose_name` **and** `help_text`. On every FK / O2O: explicit `related_name`. Use `gettext_lazy as _` for import-time strings{% if cookiecutter.use_i18n == "y" %} — [Translations](../ops/translations.md){% endif %}. Inherited Django fields keep upstream labels unless overridden.

| Attribute | Required? | Convention |
|-----------|-----------|------------|
| `verbose_name` | **Yes** | `_("words with spaces")` lowercase |
| `help_text` | **Yes** | Short English sentence (plain string, not msgid) |
| `related_name` | **Yes** on FK / O2O | Plural / role-prefixed / singular O2O / `"+"` |
| Class docstring | **Yes** | `Model to declare <noun>` |
| `Meta.verbose_name` / `_plural` | **Yes** | `_("card")` / `_("cards")` |

Never rely on Django’s default `modelname_set`:

| Situation | `related_name` | Example |
|-----------|----------------|---------|
| One-to-many | Plural child collection | `books`, `orders` |
| Multiple FKs to same model | Role-prefixed plural | `created_tasks`, `assigned_tasks` |
| One-to-one | Singular from parent | `profile` → `user.profile` |
| No reverse access | `"+"` | Lookups start from the child |

Still set `verbose_name` + `help_text` with `related_name="+"` — `"+"` only suppresses the reverse side.

### `BaseModel` (`common.models`)

{%- if cookiecutter.use_uuid_pk == "y" %}
Abstract base with a **UUID v4 primary key** and timestamps. Domain entities inherit it so IDs are not enumerable:

```python
# common/models.py
import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """Model to declare shared UUID primary key and timestamp fields"""

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False,
        verbose_name=_("id"),
        help_text="Random UUID v4 primary key. Not sequential and not guessable.",
    )
    created_at = models.DateTimeField(
        db_index=True, default=timezone.now,
        verbose_name=_("created at"), help_text="When this row was first created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("updated at"), help_text="When this row was last updated.",
    )

    class Meta:
        abstract = True
```
{%- else %}
Abstract base with **timestamps**. PKs use Django’s default `BigAutoField` unless a model declares otherwise:

```python
# common/models.py
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """Model to declare shared timestamp fields"""

    created_at = models.DateTimeField(
        db_index=True, default=timezone.now,
        verbose_name=_("created at"), help_text="When this row was first created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("updated at"), help_text="When this row was last updated.",
    )

    class Meta:
        abstract = True
```
{%- endif %}

### Constraints vs validators vs services

| Kind of rule | Prefer | Example |
|--------------|--------|---------|
| Uniqueness | `unique=True` / `UniqueConstraint` | `email = EmailField(unique=True)` |
| FK integrity | `ForeignKey` / `OneToOneField` | `Profile.user` |
| NOT NULL | `null=False` (default) | required columns |
| Cross-field DB invariant | `CheckConstraint` | `start_date < end_date` |
| Format / password UX | `*Validator` on serializer/field | `PASSWORD_VALIDATORS` |
| Workflow / “may publish if …” | Service | state machine in `services/` |

**Validators improve API messages; they are not a substitute for constraints.** Concurrent requests can both pass a serializer uniqueness check — integrity mapping turns the DB error into field-keyed `messages`. See [Validation](validation.md).

### Managers, admin, migrations

Managers under `<app>/manager/` attach as `objects = …` (normalize/create helpers). Product workflows stay in services; QuerySet helpers are called from **selectors**.

**Admin sync (required):** create/modify a model → update `<app>/admin.py` (`ModelAdmin`, `list_display`, `list_filter`, `search_fields`, `readonly_fields`). Do not put the only copy of a business rule in `save_model` — call the same service the API uses.

Migrations: one logical change when practical; never edit shipped migrations; name constraints (`name="…"`). After uniqueness/constraints, write paths use `model_*` or `map_integrity_error`. Related-row creation may use a thin [signal](signals.md); updates stay in services.

---

## Example

```python
# blogs/models/post.py
from django.db import models
from django.utils.translation import gettext_lazy as _

from {{cookiecutter.project_slug}}.blogs.enums import PostStatus
from {{cookiecutter.project_slug}}.common.models import BaseModel


class Post(BaseModel):
    """Model to declare post"""

    title = models.CharField(
        max_length=200, verbose_name=_("title"),
        help_text="Public title shown in lists and detail views.",
    )
    author = models.ForeignKey(
        "users.BaseUser", on_delete=models.CASCADE, related_name="posts",
        verbose_name=_("author"), help_text="User who wrote this post.",
    )
    status = models.CharField(
        max_length=20, choices=PostStatus.choices, default=PostStatus.DRAFT,
        verbose_name=_("status"), help_text="Publication state of the post.",
    )

    class Meta:
        verbose_name = _("post")
        verbose_name_plural = _("posts")
```

```python
# CheckConstraint (domain model — not on BaseModel)
constraints = [
    models.CheckConstraint(
        name="booking_start_date_before_end_date",
        condition=Q(start_date__lt=F("end_date")),
    )
]

# Role-prefixed FKs when the same target is linked twice
created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
    related_name="created_tasks",
    verbose_name=_("created by"), help_text="User who created this task.",
)
assignee = models.ForeignKey(
    settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
    related_name="assigned_tasks",
    verbose_name=_("assignee"), help_text="User currently assigned to this task.",
)
```

{%- if cookiecutter.use_uuid_pk == "y" %}
Domain entities (including `Profile`) subclass `BaseModel` (UUID PK + timestamps).
{%- else %}
Domain entities (including `Profile`) subclass `BaseModel` (timestamps; default `BigAutoField` PK).
{%- endif %}

---

## Anti-patterns

| Anti-pattern | Prefer |
|--------------|--------|
| Giant `models.py` | Package + one file per model |
{%- if cookiecutter.use_uuid_pk == "y" %}
| Sequential integer PKs | Inherit `BaseModel` (UUID v4 PK) |
{%- else %}
| Skipping `BaseModel` | Inherit `BaseModel` (timestamps + default PK) |
{%- endif %}
| Nested `TextChoices` on the model | `<app>/enums.py` |
| Missing `verbose_name` / `help_text` | Both on every declared field |
| FK/O2O without `related_name` / clash names | Plural / role / singular O2O / `"+"` |
| Fat `clean()` / `save()` workflows | Service (+ thin signal if needed) |
| Uniqueness only in serializers | DB unique + integrity mapping |
| Deep `models.<file>` imports from APIs | Package `__init__` exports |
| Model changed, admin stale | Sync `<app>/admin.py` in the same change |

### Checklist: adding a new model

1. `<app>/models/<name>.py` with `Model to declare …` docstring; export from `models/__init__.py`
{%- if cookiecutter.use_uuid_pk == "y" %}
2. Inherit `BaseModel` (UUID v4 PK + timestamps)
{%- else %}
2. Inherit `BaseModel` (timestamps; default `BigAutoField` PK)
{%- endif %}
3. Every field: `verbose_name` + `help_text`; every FK/O2O: explicit `related_name`
4. `Meta.verbose_name` / `verbose_name_plural` (lowercase `_()`); enums in `<app>/enums.py`
5. DB constraints the database must guarantee; manager only if helpers are real
6. Register / update admin; `makemigrations` + `migrate`
7. Selectors/services/APIs on top — not fat model methods

---

## Related

| Doc | Why |
|-----|-----|
| [Selectors](selectors.md) · [Services](services.md) | Read / write models |
| [Enums](enums.md) | `TextChoices` / `IntegerChoices` |
| [Validation](validation.md) | Constraints ↔ API messages |
| [Signals](signals.md) | Related-row invariants |
| [Domain apps](../overview/domain-apps.md) | Where `models/` sits |
