# {{cookiecutter.project_name}}

Django REST API project generated from the [Django Style Guide](https://github.com/alidanial7/django-style-guide) cookiecutter.

Based on the [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide).

## Stack

- Python 3.12 · Django 5.2 · Django REST Framework · drf-spectacular
- PostgreSQL {{cookiecutter.postgres_version}} · modular `config/settings/` layout
- Production via Docker Compose (self-hosted, not Heroku)
{%- if cookiecutter.reverse_proxy == "nginx" %}
- Nginx reverse proxy (static + media + app)
{%- elif cookiecutter.reverse_proxy == "traefik" %}
- Traefik reverse proxy
{%- endif %}
{%- if cookiecutter.use_jwt == "y" %}
- JWT authentication (`users` app)
{%- else %}
- Session authentication (`users` app)
{%- endif %}
{%- if cookiecutter.use_asgi == "y" %}
- ASGI via Uvicorn
{%- endif %}
{%- if cookiecutter.use_websockets == "y" %}
- Django Channels / WebSockets
{%- endif %}
{%- if cookiecutter.use_redis == "y" %}
- Redis 7.4.9 caching
{%- endif %}
{%- if cookiecutter.use_rabbitmq == "y" %}
- RabbitMQ message broker
{%- endif %}
{%- if cookiecutter.use_celery == "y" %}
- Celery worker + beat (broker: {{cookiecutter.celery_broker}})
{%- endif %}
{%- if cookiecutter.use_code_style == "y" %}
- Ruff linting/formatting · pre-commit hooks
{%- else %}
- flake8 linting
{%- endif %}
{%- if cookiecutter.use_ci == "y" and cookiecutter.ci_provider == "github" %}
- GitHub Actions CI (`.github/workflows/ci.yml`)
{%- elif cookiecutter.use_ci == "y" and cookiecutter.ci_provider == "gitlab" %}
- GitLab CI (`.gitlab-ci.yml`)
{%- endif %}

## Prerequisites

- Python 3.12
- Docker and Docker Compose
- virtualenv (or pyenv)

## Development setup

### 1. Enter the project

```bash
cd {{cookiecutter.project_name}}
```

### 2. Create and activate a virtualenv

```bash
python3.12 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements_dev.txt
{%- if cookiecutter.use_code_style == "y" %}
pre-commit install
{%- endif %}
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` if needed. Defaults work with the local Docker Compose services.

## Logging

Configured in `config/settings/logging.py` (see also [LOGGING.md](LOGGING.md)).

| Env var | Default | Purpose |
|---------|---------|---------|
| `DJANGO_LOGGING_LEVEL` | `INFO` | Root / console level (uppercased; invalid values fall back to `INFO`) |
| `LOG_TO_FILE` | `true` | Write JSON logs under `logs/` |
| `LOG_WHEN` | `midnight` | `TimedRotatingFileHandler` rollover |
| `LOG_INTERVAL` | `1` | Rollover interval |
| `LOG_BACKUP_COUNT` | `14` | Rotated files to keep |
| `LOG_SQL` | `false` | Log SQL via `django.db.backends` |

**Handlers**

| Handler | Destination | Levels |
|---------|-------------|--------|
| `console` | stdout | `DJANGO_LOGGING_LEVEL`+ (readable) |
| `app_file` | `logs/app/app.log` | `INFO`+ including **WARNING** (JSON lines) |
| `error_file` | `logs/error/error.log` | `ERROR`+ (JSON lines) |
| `sql_console` | stdout | only if `LOG_SQL=true` |

`django.request` errors go to **console + app_file + error_file** (when files are on).  
`logs/.gitkeep` keeps the folder in git; real log files under `logs/**` are ignored. Dirs for `app/` and `error/` are created at startup when `LOG_TO_FILE=true`.

**Request ID** — `config.request_id.RequestIdMiddleware` sets `X-Request-ID` on every response (reuses inbound header or generates uuid4). JSON file logs include `"request_id"` when a request context is active.

**Examples**

Console:

```text
2026-07-10 13:00:00 | WARNING | myapp.users.services | user 42 failed login
```

File JSON line:

```json
{"timestamp":"2026-07-10T09:30:00+00:00","level":"WARNING","logger":"myapp.users.services","message":"user 42 failed login","pathname":".../services.py","lineno":20,"funcName":"login","request_id":"…"}
```

In code: `logger = logging.getLogger(__name__)`, prefer `logger.info("user %s", user_id)` and `logger.exception(...)` in `except`. Never log secrets. Tests use quiet console-only logging (`config/django/test.py`).

### 5. Start development infrastructure

In one terminal:

```bash
./start-dev-services.sh
```

This starts:

| Service | Address |
|---------|---------|
| PostgreSQL {{cookiecutter.postgres_version}} | `localhost:5432` |
{%- if cookiecutter.use_redis == "y" %}
| Redis 7.4.9 | `localhost:6379` |
{%- endif %}
{%- if cookiecutter.use_rabbitmq == "y" %}
| RabbitMQ | `localhost:5672` |
{%- endif %}
{%- if cookiecutter.use_pgadmin == "y" %}
| pgAdmin | http://localhost:5050 |
{%- endif %}

Use `./start-dev-services.sh --clean` to wipe volumes and start fresh.

### 6. Run the application

Recommended — runs migrations, creates a default superuser, and starts the server{%- if cookiecutter.use_celery == "y" %} (plus a Celery worker in the background){%- endif %}:

```bash
python manage.py devserver
```

Or run Django only:

```bash
python manage.py migrate
python manage.py runserver
```

### Default superuser

Created automatically by `devserver` if it does not exist:

- Email: `admin@example.com`
- Password: `admin`

A `Profile` (extended user data: `bio`, `avatar`) is created automatically for every new user.
If no avatar is uploaded, the API returns the default static image at `/static/users/default_avatar.png`.
Update profile with `PATCH /api/v1/users/profile/` (`multipart/form-data` for avatar uploads).

{%- if cookiecutter.use_jwt == "y" %}
## JWT authentication

Login at `POST /api/v1/auth/jwt/login/` with `email` and `password`. Use the access token in the `Authorization: Bearer …` header.

Refresh tokens **rotate on every** `POST /api/v1/auth/jwt/refresh/` call: the response includes a new `access` and a new `refresh`. The previous refresh token is blacklisted and cannot be reused.

Logout with `POST /api/v1/auth/jwt/logout/` and body `{ "refresh": "<token>" }` to blacklist the refresh token.

| Endpoint | Auth | Notes |
|----------|------|-------|
| `POST /api/v1/auth/jwt/login/` | public | throttled (`auth`) |
| `POST /api/v1/auth/jwt/refresh/` | public | throttled (`auth`) |
| `POST /api/v1/auth/jwt/verify/` | public | throttled (`auth`) |
| `POST /api/v1/auth/jwt/logout/` | public | blacklists refresh token |
| `POST /api/v1/auth/password/change/` | JWT | current + new password |
| `POST /api/v1/auth/password/reset/` | public | emails reset uid/token (console backend locally) |
| `POST /api/v1/auth/password/reset/confirm/` | public | `{ uid, token, new_password, confirm_password }` |
| `POST /api/v1/users/register/` | public | throttled (`register`) |

| Setting | Default | Env variable |
|---------|---------|--------------|
| Access token lifetime | 15 minutes | `JWT_ACCESS_TOKEN_LIFETIME_SECONDS` |
| Refresh token lifetime | 7 days | `JWT_REFRESH_TOKEN_LIFETIME_SECONDS` |

After upgrading, run `python manage.py migrate` to create the token blacklist tables.

Password-reset emails use `EMAIL_*` / `DEFAULT_FROM_EMAIL` / `APP_DOMAIN` from `.env` (console backend by default).

> **Not included by design:** email verification, social login, and 2FA. Add those in your product layer when you need them (e.g. confirm email before issuing tokens, or integrate allauth/social providers).

{%- else %}
## Session authentication

Login at `POST /api/v1/auth/session/login/` with `email` and `password`. The server sets a session cookie.

Logout at `POST /api/v1/auth/session/logout/` (authenticated). Browser / cookie clients must send a valid CSRF token on unsafe methods (`POST`/`PATCH`/`PUT`/`DELETE`).

| Endpoint | Auth | Notes |
|----------|------|-------|
| `POST /api/v1/auth/session/login/` | public | throttled (`auth`) |
| `POST /api/v1/auth/session/logout/` | session | |
| `POST /api/v1/auth/password/change/` | session | current + new password |
| `POST /api/v1/auth/password/reset/` | public | emails reset uid/token (console backend locally) |
| `POST /api/v1/auth/password/reset/confirm/` | public | `{ uid, token, new_password, confirm_password }` |
| `POST /api/v1/users/register/` | public | creates user and logs them in |

> **Not included by design:** email verification, social login, and 2FA. Implement those in your app when required.

{%- endif %}

## URLs

| URL | Description |
|-----|-------------|
| http://localhost:8000/ | Swagger UI (**DEBUG only**) |
| http://localhost:8000/redoc/ | ReDoc (**DEBUG only**) |
| http://localhost:8000/schema/ | OpenAPI schema (**DEBUG only**) |
| http://localhost:8000/admin/ | Django admin |
| http://localhost:8000/api/v1/ | API routes (v1) |
| http://localhost:8000/api/v1/health/ | Health check (status + latency only; no secrets) |

## Project structure

```
{{cookiecutter.project_name}}/
├── config/
│   ├── django/           # base, local, production, test
│   ├── settings/         # modular settings slices (incl. logging.py)
│   ├── logging_formatters.py
│   ├── request_id.py     # X-Request-ID middleware + log filter
│   ├── urls.py
│   ├── celery.py         # Celery app factory
│   └── tasks.py
├── {{cookiecutter.project_slug}}/
│   ├── api/              # DRF urls, thin legacy exception aliases
│   ├── core/
│   ├── common/           # platform: validators/, errors/, db/integrity/, http/, services
│   ├── commands/         # management commands (devserver)
│   └── users/            # models/, validators/, errors/, services/, apis/, …
├── docker/               # Dockerfiles and entrypoints
├── docker-compose.yml    # production
├── docker-compose.dev.yml
├── start-dev-services.sh
├── scripts/
│   └── update_translations.sh
├── VALIDATION.md         # short validation layer cheat sheet
├── LOGGING.md            # logging conventions cheat sheet
└── locale/               # created by makemessages
```

Settings are composed in `config/django/base.py` from `config/settings/*.py` modules.

## Creating a new domain app

Do **not** use Django’s default `startapp` — it creates a flat layout that does not match this style guide.

**Naming:** prefer a **plural** app label, same as `users` — e.g. `blogs`, `orders`, `products` (not `blog` / `order`).

Use the custom management command instead:

```bash
python manage.py start_domain_app blogs
# or register LOCAL_APPS automatically:
python manage.py start_domain_app blogs --register
```

This scaffolds under `{{cookiecutter.project_slug}}/<name>/`:

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
    ├── test_app.py         # smoke: AppConfig importable
    └── blogs_factories.py  # commented factory stub
```

{%- if cookiecutter.use_testing == "y" %}
If the project was generated **with testing** (`pytest.ini` present), the command also adds base test stubs under `tests/`, `services/tests/`, `selector/tests/`, `apis/tests/`, and `validators/tests/`. They collect and pass out of the box; replace the placeholders as you implement features.

```bash
pytest {{cookiecutter.project_slug}}/blogs -q
```

Use `--no-tests` to skip scaffolding tests even when pytest is available.
{%- else %}
This project was generated **without testing**, so `start_domain_app` skips test stubs (no `pytest.ini`). If you add pytest later, re-run with `--force` after adding `pytest.ini`, or create tests manually.
{%- endif %}

### After scaffolding

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

4. Follow the [Validation & errors](#validation--errors) rules for codes, validators, serializers, and `map_integrity_error` on writes.

| Flag | Meaning |
|------|---------|
| *(none)* | Create files; print next steps |
| `--register` | Also append `AppConfig` to `LOCAL_APPS` |
| `--force` | Overwrite existing scaffold files in that app directory |
| `--no-tests` | Skip test stubs even if `pytest.ini` exists |

## Translations

Update translation files:

```bash
./scripts/update_translations.sh
./scripts/update_translations.sh --compile-messages
```

## Testing

{%- if cookiecutter.use_testing == "y" %}
```bash
pytest
```

Uses `config.django.test` (Postgres when `DATABASE_URL` is set, otherwise SQLite; eager Celery{%- if cookiecutter.use_celery == "y" %}{%- else %}, no Celery{%- endif %}). Default tests cover health, auth, register, profile, user services, and selectors. CI runs against Postgres.
{%- else %}
Testing tooling was not included at project generation. Add pytest later if needed.
{%- endif %}

{%- if cookiecutter.use_ci == "y" %}
## Continuous integration

{%- if cookiecutter.ci_provider == "github" %}
GitHub Actions workflow: [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

Runs on pushes/PRs to `main`/`master`: lint, mypy, `manage.py check`,{%- if cookiecutter.use_testing == "y" %} and `pytest` (with coverage; Postgres service){%- endif %}.
{%- elif cookiecutter.ci_provider == "gitlab" %}
GitLab CI config: [`.gitlab-ci.yml`](.gitlab-ci.yml).

Pipeline stage `check`: lint, mypy, `manage.py check`,{%- if cookiecutter.use_testing == "y" %} and `pytest` (Postgres service){%- endif %}.
{%- endif %}

CI uses{%- if cookiecutter.use_testing == "y" %} `config.django.test` with a Postgres service{%- else %} `config.django.local` with a SQLite `DATABASE_URL`{%- endif %}.
{%- endif %}

## Validation & errors

This project separates **platform** concerns (`common`) from **domain** concerns (each app, e.g. `users`).  
A short cheat sheet lives in [VALIDATION.md](VALIDATION.md). The sections below explain how to define and use each layer.

### Layer map

| Layer | Location | Responsibility |
|-------|----------|----------------|
| Pure checks | `common/validators/` or `<app>/validators/` | `is_*` → `bool` only (no messages, no exceptions) |
| Platform codes | `common/errors/codes.py` → `ErrorCode` | Shared machine codes (`required`, `unique`, `not_null`, …) |
| Domain codes | `<app>/errors/codes.py` → e.g. `UserErrorCode` | App-specific codes (password, …). Codes only — never validators |
| Raising validators | `<app>/validators/` | `@deconstructible` classes that raise Django `ValidationError` with `code=` |
| Serializers | `<app>/apis/...` | Input shape + cross-field `validate()` only |
| Services / writes | `<app>/services/` + `common/services.py` | Business rules + persistence; always map integrity errors |
| Integrity mapping | `common/db/integrity/` | `IntegrityError` → field-keyed Django `ValidationError` / controlled `APIException` |
| API envelope | `common/http/` (`api_response` + `api_exception_handler`) | Single success/error response shape |

**Do not** put domain password rules in `common`, raising validators in `errors/`, or business/permission rules in serializers/views.

### API response envelope

Success and error responses share one outer shape. Use `api_response(...)` from `common.http` in views (do not return raw `Response(data)` for API payloads).

**Success**

```json
{
  "success": true,
  "status": 200,
  "result": { "email": "a@example.com" },
  "messages": {}
}
```

**Error**

```json
{
  "success": false,
  "status": 400,
  "result": [],
  "messages": {
    "email": [
      { "message": "email already exists.", "code": "unique" }
    ],
    "confirm_password": [
      { "message": "confirm password is not equal to password", "code": "password_mismatch" }
    ]
  }
}
```

Each error field maps to a list of `{ "message", "code" }` objects. If a raiser omitted `code=`, the handler falls back to `"invalid"`. Unexpected server errors use `"server_error"` and never leak internals.

Wired in `config/settings/drf.py` to `common.http.exception_handler.api_exception_handler`.  
`api/exception_handlers.py` is a thin legacy alias only — do not add a second implementation.

Auth/register endpoints are rate-limited via DRF `ScopedRateThrottle` (`auth`, `register`, `password_reset` rates in `config/settings/drf.py`). Prefer Redis (`use_redis=y`) in multi-worker production so throttle counters are shared.

### 1. Platform error codes (`common`)

Use for integrity mapping and shared input problems:

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

### 2. Domain error codes (per app)

Password and other identity codes live under `users`:

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

Add new apps the same way: `<app>/errors/codes.py` with an app-prefixed enum name (e.g. `OrdersErrorCode`). Never reuse the platform name `ErrorCode` for domain codes.

### 3. Pure validators (`is_*`)

**Generic (any app):** add helpers under `common/validators/` (see the commented `is_slug` example in `common/validators/string.py`).

```python
def is_slug(value: str) -> bool:
    return isinstance(value, str) and _SLUG_RE.fullmatch(value) is not None
```

**Domain (users passwords):** pure checks live at the top of `users/validators/password.py` next to the raising validators:

```python
def is_password_with_number(value: str) -> bool:
    ...
```

Naming separates concerns inside one file: `is_*` (bool) vs `*Validator` (raises).

Rules for every pure check: return `bool` only; no `ValidationError`, no `gettext`, no user-facing messages.

### 4. Raising field validators (`*Validator`)

Use Django’s `ValidationError` (not DRF’s) so the same class works on models and serializers.  
User-facing `_()` / `gettext_lazy` msgids stay **lowercase**. Parameterized messages use `params=` (do not pre-format with `%`):

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
```

Attach on the serializer:

```python
password = serializers.CharField(validators=PASSWORD_VALIDATORS)
```

**Password policy (API + Django auth share the same domain rules):**

| Path | Setting / list | Used for |
|------|----------------|----------|
| API input | `users.validators.PASSWORD_VALIDATORS` | Register / DRF fields |
| Django auth | `AUTH_PASSWORD_VALIDATORS` in `config/settings/auth.py` | Admin / `set_password` (includes `Password*DjangoValidator` adapters + Django built-ins) |

Wire domain validators into `AUTH_PASSWORD_VALIDATORS` via the `Password*DjangoValidator` adapters (already configured) so admin/`set_password` and API share the same rules.

### 5. Serializers (shape + object rules only)

- Field validators: reuse domain `*Validator` lists.
- Cross-field rules: `validate()` with **field-keyed** errors and `gettext_lazy` messages.
- Platform vs domain codes as appropriate:

```python
# missing input → ErrorCode.REQUIRED (platform)
# password mismatch → UserErrorCode.PASSWORD_MISMATCH (domain)
raise serializers.ValidationError(
    {"confirm_password": [_("confirm password is not equal to password")]},
    code=UserErrorCode.PASSWORD_MISMATCH,
)
```

Do not put uniqueness checks or permission logic in serializers — uniqueness is enforced by the DB and mapped via integrity (below).

### 6. Services and integrity mapping

Every persistence path must either:

1. go through `common.services.model_create` / `model_save` / `model_update`, or  
2. catch `IntegrityError` and call `map_integrity_error` (raise-only; never returns):

```python
from django.db import IntegrityError
from {{cookiecutter.project_slug}}.common.db.integrity import map_integrity_error
from {{cookiecutter.project_slug}}.common.services import model_create

# Preferred for ordinary model writes:
instance = model_create(model_class=MyModel, data={...})

# Manager-based creates that bypass model_create:
try:
    return MyModel.objects.create(...)
except IntegrityError as error:
    map_integrity_error(error, model=MyModel)
    raise
```

`common/db/integrity/` prefers Postgres `pgcode` (`23505` unique, `23502` not null, `23503` FK) with SQLite message fallback. Known columns become **field-keyed** errors in `messages`.

DB constraints (unique / FK / NOT NULL) remain the final authority; validators are UX, not a substitute for constraints.

### 7. How to add a new field rule (checklist)

1. **Pure check** — generic → `common/validators/`; domain → `<app>/validators/` as `is_*`.
2. **Code** — platform → `common.errors.codes.ErrorCode`; domain → `<app>/errors/codes.py`.
3. **Raising validator** — `@deconstructible` in `<app>/validators/`, Django `ValidationError` + `code=`.
4. **Wire it** — model field when the rule is universal; serializer field for API input; cross-field only in `validate()`.
5. **Persist safely** — add a DB constraint for uniqueness/FK/null; ensure writes use `model_*` helpers or `map_integrity_error`.

### Example layout

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

## Code quality

{%- if cookiecutter.use_code_style == "y" %}
This project uses [pre-commit](https://pre-commit.com/) to run checks before each commit. Hook groups were chosen at project generation; see `.pre-commit-config.yaml`.

```bash
pre-commit install          # once, after pip install
pre-commit run --all-files  # run every hook on the whole tree
```

You can also run tools directly:

```bash
ruff check .
ruff format .
```

### Pre-commit hook groups

| Group | What it does |
|-------|----------------|
| **File hygiene** (`pre-commit-hooks`) | Trims trailing whitespace, fixes EOF newlines, validates JSON/YAML/XML, blocks debug statements and merge conflicts, detects private keys, and checks Python AST. |
| **pyupgrade** | Rewrites older Python syntax to match Python 3.12 (e.g. `list[str]` instead of `List[str]`). |
| **Ruff** | Lints with Ruff (`ruff check --fix`) and formats with `ruff format`. |
| **pydoclint** | Enforces [Google-style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) docstrings on functions and methods. |
| **django-translation-lint** | Ensures Django `gettext` / `_()` strings use lowercase text (i18n convention). |

To change which groups are active, edit `.pre-commit-config.yaml` and remove or comment out a `repo:` block, then run `pre-commit autoupdate` if you bump versions.
{%- else %}
```bash
flake8
mypy .
```
{%- endif %}

## Production (Docker Compose)

Self-hosted production — no Heroku or third-party PaaS.

### 1. Configure environment

```bash
cp .env.example .env
```

Set `DJANGO_SETTINGS_MODULE=config.django.production`, a strong `SECRET_KEY`, and `ALLOWED_HOSTS`.

When serving HTTPS, also set `SESSION_COOKIE_SECURE=true`, `CSRF_COOKIE_SECURE=true`, `SECURE_SSL_REDIRECT=true`, `SECURE_HSTS_SECONDS=31536000`, and `CSRF_TRUSTED_ORIGINS`.

{%- if cookiecutter.use_sentry == "y" %}
Optionally set `SENTRY_DSN` to enable Sentry (only activates when the DSN is set).
{%- endif %}

### 2. Build and start

```bash
docker compose up --build -d
```

This starts:

- PostgreSQL {{cookiecutter.postgres_version}} (internal network only — not published)
{%- if cookiecutter.use_redis == "y" %}
- Redis
{%- endif %}
{%- if cookiecutter.use_rabbitmq == "y" %}
- RabbitMQ
{%- endif %}
{%- if cookiecutter.use_asgi == "y" %}
- Django (Uvicorn on port 8000)
{%- else %}
- Django (gunicorn on port 8000)
{%- endif %}
{%- if cookiecutter.use_celery == "y" %}
- Celery worker
- Celery beat
{%- endif %}
{%- if cookiecutter.reverse_proxy == "nginx" %}
- Nginx on port 80 (proxies app; serves `/static/` and `/media/`)
{%- elif cookiecutter.reverse_proxy == "traefik" %}
- Traefik on port 80 (proxies app; configure TLS for real domains)
{%- endif %}

{%- if cookiecutter.reverse_proxy == "none" %}
App: http://localhost:8000  
Uploaded media is served by Django from the `media-data` volume when no reverse proxy was selected. Prefer regenerating with `reverse_proxy=nginx` for production traffic.
{%- elif cookiecutter.reverse_proxy == "nginx" %}
App: http://localhost/  
{%- else %}
App: http://localhost/  
{%- endif %}

The production Compose file runs the image as built (no source bind-mount). Rebuild after code changes: `docker compose up --build -d`.

## Useful commands

| Command | Description |
|---------|-------------|
| `make install` | Install `requirements_dev.txt` |
| `make up` / `make down` | Start/stop local Docker infra |
| `make test` | Run pytest |
| `make lint` | Lint |
| `make migrate` | Apply migrations |
| `make runserver` | `manage.py devserver` |
| `./start-dev-services.sh` | Start dev Docker services |
| `python manage.py start_domain_app <name>` | Scaffold a domain app (style-guide layout) |
| `python manage.py start_domain_app <name> --register` | Scaffold + add to `LOCAL_APPS` |
| `python manage.py devserver` | Migrate, superuser, runserver{%- if cookiecutter.use_celery == "y" %}, Celery{%- endif %} |
| `python manage.py runserver` | Django dev server only |
| `./scripts/update_translations.sh` | Update `.po` translation files |
| `docker compose up --build -d` | Start production stack |
