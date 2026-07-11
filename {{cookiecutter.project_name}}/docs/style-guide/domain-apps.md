# Domain apps

Do **not** use Django’s default `startapp`. It creates a flat layout that does not match this style guide.

## Naming

Prefer a **plural** app label, same as `users`:

| Prefer | Avoid |
|--------|--------|
| `blogs` | `blog` |
| `orders` | `order` |
| `products` | `product` |

Use lowercase `snake_case`: `^[a-z][a-z0-9_]*$`.

## Scaffold command

```bash
python manage.py start_domain_app blogs
# also append AppConfig to LOCAL_APPS:
python manage.py start_domain_app blogs --register
```

### Flags

| Flag | Meaning |
|------|---------|
| *(none)* | Create files; print next steps |
| `--register` | Append `AppConfig` to `LOCAL_APPS` in `config/settings/apps.py` |
| `--force` | Overwrite existing scaffold files in that app directory |
| `--no-tests` | Skip test stubs even if `pytest.ini` exists |

{%- if cookiecutter.use_testing == "y" %}
This project was generated **with testing** (`pytest.ini` present). The command adds base test stubs under `tests/`, `services/tests/`, `selector/tests/`, `apis/tests/`, and `validators/tests/`.

```bash
pytest {{cookiecutter.project_slug}}/blogs -q
```
{%- else %}
This project was generated **without testing**, so `start_domain_app` skips test stubs. If you add pytest later, re-run with `--force` after adding `pytest.ini`, or create tests manually.
{%- endif %}

## Scaffolded layout

```text
blogs/
├── apps.py                 # BlogsConfig → {{cookiecutter.project_slug}}.blogs
├── admin.py
├── constants.py
├── models/                 # one module per model; export from __init__.py
├── manager/
├── selector/               # read queries (+ tests/ when testing is on)
├── services/               # writes + business rules (+ tests/)
├── apis/                   # DRF APIs / serializers (+ tests/)
├── urls/
│   └── blogs.py            # urlpatterns for this app
├── validators/             # domain is_* + *Validator (+ tests/)
├── errors/
│   └── codes.py            # BlogsErrorCode (codes only)
├── signals/
├── utils/
├── migrations/
└── tests/                  # only if project has pytest.ini
    ├── test_app.py
    └── blogs_factories.py
```

## Folder responsibilities

| Folder | Responsibility |
|--------|----------------|
| `models/` | Django models; one file per model; re-export in `__init__.py` |
| `manager/` | Custom managers / querysets when needed |
| `selector/` | **Read-only** query functions |
| `services/` | **Writes** and business rules |
| `apis/` | APIViews + input/output serializers (group by feature) |
| `urls/` | URLConf modules included from `api/urls.py` |
| `validators/` | Pure `is_*` + raising `*Validator` |
| `errors/` | Domain `StrEnum` codes only — never raise from here |
| `signals/` | Side effects (keep minimal) |
| `constants.py` | Tags, magic strings, static paths |
| `utils/` | App-local helpers that are neither selector nor service |

## After scaffolding

1. **Register the app** (skip if you used `--register`):

```python
# config/settings/apps.py
LOCAL_APPS = [
    ...
    "{{cookiecutter.project_slug}}.blogs.apps.BlogsConfig",
]
```

2. **Wire URLs**:

```python
# {{cookiecutter.project_slug}}/api/urls.py
path("blogs/", include(("{{cookiecutter.project_slug}}.blogs.urls.blogs", "blogs"))),
```

3. Add models under `models/`, then:

```bash
python manage.py makemigrations blogs
python manage.py migrate
```

4. Follow [Validation & errors](validation-and-errors.md) for codes, validators, serializers, and `map_integrity_error` on writes.

## Feature grouping under `apis/`

Mirror `users`: group by feature, not by HTTP verb.

```text
users/apis/
├── auth/           # login, logout, password
└── users/
    ├── register/
    └── profile/
```

Each feature folder typically has `*_apis.py`, `*_serializers.py`, and optional `tests/`.

## Reference app: `users`

Use `{{cookiecutter.project_slug}}.users` as the canonical example for:

- models + managers
- selectors + services
- validators + error codes
- auth-aware APIs (`ApiAuthMixin`)
- Swagger tags in `constants.py`
- signals creating related `Profile` rows
