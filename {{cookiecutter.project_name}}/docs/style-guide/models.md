# Models

## Layout

Put models in a **package**, one module per model, and re-export from `__init__.py`:

```text
users/models/
├── __init__.py      # from .base_user import BaseUser; from .profile import Profile
├── base_user.py
└── profile.py
```

```python
# models/__init__.py
from .base_user import BaseUser
from .profile import Profile

__all__ = ["BaseUser", "Profile"]
```

Import models from the package root elsewhere: `from ...users.models import BaseUser`.

## `BaseModel` (`common.models`)

Abstract base with `created_at` / `updated_at`. Prefer inheriting from it for domain models that need timestamps.

```python
from {{cookiecutter.project_slug}}.common.models import BaseModel

class Post(BaseModel):
    title = models.CharField(max_length=200)
    ...
```

`common.models.RandomModel` is an example of **DB CheckConstraint** usage (start/end dates) — keep that pattern for rules the database must enforce.

## Constraints vs validators

| Kind of rule | Prefer |
|--------------|--------|
| Uniqueness, FK, NOT NULL | DB constraint / field options + integrity mapping |
| Cross-field DB invariants | `CheckConstraint` / unique_together / UniqueConstraint |
| Format / password policy | Field validators (`*Validator`) + serializers |
| Business workflows | Services |

Validators improve API messages; they are **not** a substitute for constraints.

## Managers

Custom managers live under `<app>/manager/` (e.g. `users/manager/user_manager.py`) and are attached on the model. Keep create helpers thin; complex business creation still goes through **services**.

## Admin

Register models in `<app>/admin.py`. Keep admin as an operator UI — do not put product business rules only in admin hooks.

## Migrations

Run migrations after model changes:

```bash
python manage.py makemigrations <app_label>
python manage.py migrate
```

App label matches the plural package name (`users`, `blogs`, …).
