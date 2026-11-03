# File manager

Centralized uploads via `{{cookiecutter.project_slug}}.file_manager`. Other domains **FK to `ManagedFile`** — do not add ad-hoc `FileField` / `ImageField` on domain models.

---

## Rules

| Do | Don't |
|----|--------|
| Upload through `create_managed_file` | Call `serializer.save()` / assign raw uploads in APIs |
| Store binary metadata on `ManagedFile` only | Scatter `FileField`s across apps |
| Point domain FKs at `ManagedFile` | Duplicate storage paths / mime / size fields |
| Use `FileCategory` from `enums.py` | Nest category choices on the model |
| Rely on `post_delete` for disk cleanup | Manually `file.delete()` in every service |

User-scoped only: each row has an `owner` (AUTH_USER_MODEL). There is no clinic / org FK in this scaffold.

Categories (`enums.FileCategory`): `avatar`, `image`, `document`, `other`. Size / extension / MIME / default publicity live in `constants.CATEGORY_FILE_RULES`.

---

## Package layout

```text
file_manager/
├── enums.py              # FileCategory
├── constants.py          # limits + CATEGORY_FILE_RULES
├── types.py              # CreateManagedFileData
├── models/file.py        # ManagedFile
├── services/file_services.py
├── selectors/file_selectors.py
├── validators/file.py
├── errors/codes.py
├── signals/file_signals.py   # post_delete → wipe storage
├── apis/files/               # list/create, detail/delete, download
└── urls/file_manager_url.py  # mounted at /api/v1/files/
```

---

## FK pattern (domain models)

Prefer a nullable FK (or O2O) to `ManagedFile` instead of a local file field:

```python
# e.g. pets/models/pet.py — illustrative
from django.db import models
from django.utils.translation import gettext_lazy as _

from {{cookiecutter.project_slug}}.common.models import BaseModel
from {{cookiecutter.project_slug}}.file_manager.models import ManagedFile


class Pet(BaseModel):
    """Model to declare pet"""

    photo = models.ForeignKey(
        ManagedFile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pet_photos",
        verbose_name=_("photo"),
        help_text="Managed upload for the pet photo.",
    )
```

Flow: client uploads to `POST /api/v1/files/` → receives `id` → PATCH/create the domain resource with that id. Optionally assert `category` / `owner` in the domain service before attaching.

In-tree reference: `users.Profile.avatar` is an FK to `ManagedFile` (added in `users.0002` after `file_manager.0001` to avoid a circular migration). Register/profile multipart still accepts an upload; the users service calls `create_managed_file` then attaches the row.

---

## `create_managed_file`

```python
from {{cookiecutter.project_slug}}.file_manager.enums import FileCategory
from {{cookiecutter.project_slug}}.file_manager.services import create_managed_file
from {{cookiecutter.project_slug}}.file_manager.types import CreateManagedFileData

# From an API (preferred): serializer → TypedDict → service
managed = create_managed_file(user=request.user, data=serializer.validated_data)

# From another service (discrete args)
managed = create_managed_file(
    user=user,
    file_obj=uploaded,
    title="Avatar",
    category=FileCategory.AVATAR,
)
```

- Validates via `validate_managed_file` (category rules).
- Persists with `model_create` (`full_clean` + integrity map).
- If `is_public` is omitted, defaults from `is_category_public(category)` (avatars public by default).
- Delete with `delete_managed_file` → `model_delete` (or `.delete()`); signal removes the bytes.

---

## HTTP surface

| Method | Path | Auth |
|--------|------|------|
| `GET` / `POST` | `/api/v1/files/` | Authenticated (own files) |
| `GET` / `DELETE` | `/api/v1/files/<id>/` | Owner / admin |
| `GET` | `/api/v1/files/<id>/download/` | Public if `is_public`; else owner / admin |

Download: `FileResponse` when `DEBUG`; production uses `X-Accel-Redirect` to `PROTECTED_STORAGE_URL`.

---

## When to open this page

Adding uploads, attaching files to domain models, or changing category rules / download behaviour. Routine CRUD elsewhere: follow `users/` + `.cursor/rules/file-manager.mdc`.
