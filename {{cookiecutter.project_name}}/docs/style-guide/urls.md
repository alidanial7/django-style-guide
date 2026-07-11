# URLs & routing

## Top-level

`config/urls.py` mounts:

| Path | Purpose |
|------|---------|
| `/admin/` | Django admin |
| `/api/v1/` | Versioned API (`{{cookiecutter.project_slug}}.api.urls`) |
| `/`, `/redoc/`, `/schema/` | Swagger / ReDoc / OpenAPI schema (**DEBUG only**) |

Media serving depends on `DEBUG` and reverse-proxy choice — see [Docker & production](docker-and-production.md).

## API package router

`{{cookiecutter.project_slug}}/api/urls.py` includes per-app URL modules:

```python
urlpatterns = [
    path("", include(("{{cookiecutter.project_slug}}.core.urls", "core"))),
    path("auth/", include(("{{cookiecutter.project_slug}}.users.urls.auth", "auth"))),
    path("users/", include(("{{cookiecutter.project_slug}}.users.urls.users", "users"))),
    # path("blogs/", include(("{{cookiecutter.project_slug}}.blogs.urls.blogs", "blogs"))),
]
```

## Per-app `urls/`

Keep URLConf in `<app>/urls/<name>.py` with `app_name` and named routes:

```python
# users/urls/users.py
app_name = "users"

urlpatterns = [
    path("register/", UsersRegisterApi.as_view(), name="register"),
    path("profile/", UsersProfileApi.as_view(), name="profile"),
]
```

Split auth and resource routes when they grow (as `users` does with `urls/auth.py` and `urls/users.py`).

## Versioning

All public HTTP APIs live under `/api/v1/`. When introducing v2, add a new include path and keep v1 stable.

## Naming

- Prefer trailing slashes (Django default).
- Use kebab-case in paths when multi-word (`password/reset/confirm/`).
- Give every route a stable `name=` for `reverse()`.
