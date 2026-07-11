# 🧩 Domain apps

> How to create and grow a **product domain** package (`users`, `blogs`, `orders`, …) so it matches this style guide.
>
> **Never** use Django’s default `startapp` — its flat `models.py` / `views.py` layout fights every other doc in this folder.

---

## 🎯 What is a “domain app”?

A domain app owns one business area end-to-end:

```text
HTTP  →  apis/ + urls/
reads →  selector/
writes → services/
shape →  models/ + manager/
rules →  validators/ + errors/
glue  →  constants.py, signals/, utils/
```

```mermaid
flowchart TB
    subgraph DomainApp["blogs/ (example domain app)"]
        URLs[urls/]
        APIs[apis/]
        SEL[selector/]
        SVC[services/]
        MOD[models/]
        VAL[validators/ + errors/]
    end

    Client --> URLs --> APIs
    APIs -->|read| SEL
    APIs -->|write| SVC
    SEL --> MOD
    SVC --> MOD
    APIs --> VAL
    SVC --> VAL
```

`users` is the **reference implementation**. Copy its patterns; do not invent a parallel layout.

---

## 🏷️ Naming rules

### Plural app labels

Match Django’s common style and this template’s `users` app:

| ✅ Prefer | ❌ Avoid |
|----------|---------|
| `blogs` | `blog` |
| `orders` | `order` |
| `products` | `product` |
| `order_items` | `OrderItems` / `order-items` |

### Technical constraints (`start_domain_app`)

| Rule | Detail |
|------|--------|
| Pattern | `^[a-z][a-z0-9_]*$` — lowercase Python identifier |
| Reserved | `api`, `common`, `commands`, `config`, `core`, `django`, `manage`, `test`, `tests` |
| Package path | `{{cookiecutter.project_slug}}.<name>` |
| AppConfig | `<PascalName>Config` (e.g. `blogs` → `BlogsConfig`) |
| Error enum | `<PascalName>ErrorCode` (e.g. `BlogsErrorCode`) |

```bash
# ✅
python manage.py start_domain_app blogs
python manage.py start_domain_app order_items

# ❌ rejected or discouraged
python manage.py start_domain_app Blog
python manage.py start_domain_app common    # reserved
python manage.py start_domain_app my-app    # invalid identifier
```

---

## 🚀 Scaffold with `start_domain_app`

```bash
python manage.py start_domain_app blogs
# create files AND append AppConfig to LOCAL_APPS:
python manage.py start_domain_app blogs --register
```

### Flags

| Flag | Meaning | When to use |
|------|---------|-------------|
| *(none)* | Write scaffold files; print next steps | Default — review files before registering |
| `--register` | Also append `"….BlogsConfig"` to `LOCAL_APPS` | When you are sure of the name |
| `--force` | Overwrite existing scaffold files in that directory | Re-scaffold after enabling tests, or recover a broken tree — **destructive** |
| `--no-tests` | Skip test stubs even if `pytest.ini` exists | Rare; prefer keeping stubs |

{%- if cookiecutter.use_testing == "y" %}
### Testing stubs

This project was generated **with testing** (`pytest.ini` present). The command also creates base stubs under:

- `tests/` (smoke + factory stub)
- `services/tests/`, `selector/tests/`, `apis/tests/`, `validators/tests/`

They collect and pass out of the box; replace placeholders as you implement features.

```bash
pytest {{cookiecutter.project_slug}}/blogs -q
```
{%- else %}
### Testing stubs

This project was generated **without testing**, so `start_domain_app` skips test stubs (no `pytest.ini`). If you add pytest later, re-run with `--force` after adding `pytest.ini`, or create tests manually.
{%- endif %}

---

## 📂 Scaffolded layout (every folder explained)

```text
blogs/
├── apps.py                 # BlogsConfig; ready() for signals later
├── admin.py                # Django admin registrations
├── constants.py            # tags / paths / literals → see constants.md
├── models/                 # one module per model; export from __init__.py
├── manager/                # custom managers / querysets
├── selector/               # READ queries (+ tests/)
├── services/               # WRITE + business rules (+ tests/)
├── apis/                   # DRF views + serializers, grouped by feature (+ tests/)
├── urls/
│   └── blogs.py            # urlpatterns + app_name for this app
├── validators/             # is_* pures + *Validator raisers (+ tests/)
├── errors/
│   └── codes.py            # BlogsErrorCode StrEnum — codes ONLY
├── signals/                # mechanical side effects → see signals.md
├── utils/                  # leftovers that are neither selector nor service
├── migrations/
└── tests/                  # only if pytest.ini exists
    ├── test_app.py
    └── blogs_factories.py
```

### Responsibility cheat sheet

| Path | ✅ Does | ❌ Does not |
|------|--------|------------|
| `models/` | Fields, constraints, relations | HTTP, complex workflows |
| `manager/` | Reusable QuerySet/Manager methods | Call external APIs / send email as “business feature” |
| `selector/` | Reads, annotations, derived URLs | `.create()` / `.save()` as the main job |
| `services/` | Writes, transactions, domain rules | Parse `request.data` / return `Response` |
| `apis/` | Auth, validate input, call selector/service, `api_response` | Fat ORM blocks |
| `urls/` | Path → view mapping | Business logic |
| `validators/` | Field-level pure + raising checks | Cross-aggregate workflows |
| `errors/codes.py` | Stable machine codes | `raise ValidationError` |
| `signals/` | Idempotent mechanical follow-ups | User-facing API validation |
| `constants.py` | Shared literals | Env settings / error codes |
| `utils/` | Tiny pure helpers | Hidden second service layer |

Deep dives: [Models](models.md), [Selectors](selectors.md), [Services](services.md), [APIs](apis.md), [Validation](validation-and-errors.md), [Constants](constants.md), [Signals](signals.md).

---

## ✅ After scaffolding — checklist

```mermaid
flowchart LR
    A[start_domain_app] --> B[Register LOCAL_APPS]
    B --> C[Wire api/urls.py]
    C --> D[Add models + migrate]
    D --> E[Selectors / services / apis]
    E --> F[Validators + error codes]
    F --> G[Tests]
```

### 1. Register the app

Skip if you used `--register`.

```python
# config/settings/apps.py
LOCAL_APPS = [
    ...
    "{{cookiecutter.project_slug}}.blogs.apps.BlogsConfig",
]
```

### 2. Wire URLs into the versioned API

```python
# {{cookiecutter.project_slug}}/api/urls.py
from django.urls import include, path

urlpatterns = [
    path("", include(("{{cookiecutter.project_slug}}.core.urls", "core"))),
    path("auth/", include(("{{cookiecutter.project_slug}}.users.urls.auth", "auth"))),
    path("users/", include(("{{cookiecutter.project_slug}}.users.urls.users", "users"))),
    path("blogs/", include(("{{cookiecutter.project_slug}}.blogs.urls.blogs", "blogs"))),
]
```

Public base path becomes: `/api/v1/blogs/…` — details in [URLs](urls.md).

### 3. Add models and migrate

```bash
# create models under blogs/models/, export them in models/__init__.py
python manage.py makemigrations blogs
python manage.py migrate
```

### 4. Implement layers in order (recommended)

1. **Model + constraints** — DB is source of truth for uniqueness/FK/null  
2. **Error codes** in `errors/codes.py`  
3. **Validators** if field rules need friendly API messages  
4. **Services** for writes, **selectors** for reads  
5. **APIs + serializers** + `@extend_schema`  
6. **Tests** next to each layer  

### 5. Validation & integrity on every write

Follow [Validation & errors](validation-and-errors.md): domain codes, `is_*` / `*Validator`, and `model_create` / `map_integrity_error` on persistence.

Remember **deny-by-default**: public APIs need `permission_classes = [AllowAny]`; authenticated ones use `ApiAuthMixin` — see [Permissions](permissions.md) / [Security](security.md).

---

## 🗂️ Feature grouping under `apis/`

Group by **feature**, not by HTTP verb or by “all serializers in one file”.

### Reference: `users`

```text
users/apis/
├── auth/                      # login, logout, password
│   ├── auth_jwt_apis.py       # or auth_session_apis.py
│   ├── auth_password_apis.py
│   ├── auth_serializers.py
│   └── tests/
└── users/
    ├── register/
    │   ├── users_register_apis.py
    │   ├── users_register_serializers.py
    │   └── tests/
    └── profile/
        ├── users_profile_apis.py
        ├── users_profile_serializers.py
        └── tests/
```

### Suggested layout for `blogs`

```text
blogs/apis/
├── posts/
│   ├── posts_apis.py
│   ├── posts_serializers.py
│   └── tests/
└── comments/
    ├── comments_apis.py
    ├── comments_serializers.py
    └── tests/
```

Each feature folder typically contains:

| File | Role |
|------|------|
| `*_apis.py` | `APIView` classes |
| `*_serializers.py` | Input + output serializers |
| `tests/` | HTTP / permission tests for that feature |

Naming prefix (`users_profile_…`, `posts_…`) keeps grepping and imports obvious.

---

## 🔗 URLs inside the app

Scaffold creates:

```python
# blogs/urls/blogs.py
from django.urls import path

app_name = "blogs"

urlpatterns = [
    # path("", SomeApi.as_view(), name="list"),
]
```

Split modules when the surface grows (like `users/urls/auth.py` + `users/urls/users.py`), and include each from `api/urls.py`.

---

## 🧪 Errors package stub

Scaffold creates codes-only enum — fill as features land:

```python
# blogs/errors/codes.py
from enum import StrEnum


class BlogsErrorCode(StrEnum):
    """Domain machine codes for blogs. Add codes as features grow."""

    # POST_NOT_PUBLISHED = "post_not_published"
```

Never put raising validators in `errors/`.

---

## 📘 Worked mini-flow: first endpoint on a new app

Assume `blogs` is scaffolded and registered.

**1. Model** — `blogs/models/post.py` + export in `models/__init__.py`  
**2. Selector** — `list_posts()` in `selector/post_selectors.py` (add `PostFilter` in `apis/posts/posts_filters.py` only if the list accepts filters)  
**3. API** — `PostsListApi` in `apis/posts/posts_apis.py` returning `api_response`  
**4. URL** — `path("posts/", PostsListApi.as_view(), name="posts-list")`  
**5. Include** already under `/api/v1/blogs/`  
**6. Test** — `apis/posts/tests/test_posts_list.py`

Write path (`POST` create) adds `services/` + validators + integrity mapping before exposing the endpoint.

---

## ❌ Common mistakes

| Mistake | Fix |
|---------|-----|
| `django-admin startapp blogs` | `python manage.py start_domain_app blogs` |
| Singular `blog` app label | Plural `blogs` |
| Putting views in `views.py` at app root | Use `apis/<feature>/` |
| One giant `serializers.py` for the whole app | Per-feature serializer modules |
| Business rules in `apis/` | Move to `services/` |
| Registering app but forgetting `api/urls.py` | No route → 404; wire the include |
| Domain error codes named `ErrorCode` | Use `BlogsErrorCode` — `ErrorCode` is platform-only in `common` |

---

## 🔗 Related docs

| Doc | Why |
|-----|-----|
| [Project structure](project-structure.md) | Where the package sits in the repo |
| [Architecture](architecture.md) | Layer decision tree |
| [URLs](urls.md) | How includes and versioning work |
| [APIs](apis.md) | View/serializer rules |
| Living example | The real `{{cookiecutter.project_slug}}/users/` tree in this repo |
