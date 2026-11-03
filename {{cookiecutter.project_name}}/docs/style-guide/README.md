# Style guide

Conventions for this codebase. Inspired by [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide).

Agents: start at [`AGENTS.md`](../../AGENTS.md) + `.cursor/rules/` — open **one** page below only when a rule is not enough.

## Layout

```text
docs/style-guide/
├── overview/   # architecture, folders, scaffolding
├── domain/     # models → APIs, validation, errors
├── http/       # envelope, auth, pagination, …
└── ops/        # settings, tests, docker, …
```

## Principles

1. Domain apps own business rules.
2. Selectors read; services write.
3. APIs are glue — InputSerializer → service(`data=` TypedDict) / selector → `api_response`.
4. DB constraints own uniqueness / FK / NOT NULL; validators are UX.
5. One envelope: `success`, `status`, `result`, `messages`.
6. Platform in `common/`; domain codes/validators in the app.
7. Deny by default — `IsAuthenticated` unless `AllowAny`.
8. Lists: selector + pagination; filters in `apis/` as `*_search_filters.py` after `list_*()`.
9. TypedDict + `model_*` — no dataclass DTOs; serializers never `save()`.

## Index

### `overview/`

| Doc | Topic |
|-----|--------|
| [Architecture](overview/architecture.md) | Layers, request flow |
| [Project structure](overview/project-structure.md) | Folders, `config/` |
| [Domain apps](overview/domain-apps.md) | `start_domain_app` |

### `domain/`

| Doc | Topic |
|-----|--------|
| [Models](domain/models.md) | `BaseModel`, labels, constraints |
| [Enums](domain/enums.md) | Choices in `enums.py` |
| [Selectors](domain/selectors.md) | Reads |
| [Types](domain/types.md) | TypedDict inputs |
| [Services](domain/services.md) | Writes, `model_*` |
| [APIs & serializers](domain/apis.md) | Route-mirrored `apis/` |
| [URLs & routing](domain/urls.md) | Versioned API |
| [Validation](domain/validation.md) | `is_*` / `*Validator` |
| [Errors](domain/errors.md) | Codes, integrity |
| [Constants](domain/constants.md) | App literals |
| [Signals](domain/signals.md) | Mechanical side effects |

### `http/`

| Doc | Topic |
|-----|--------|
| [API response envelope](http/api-envelope.md) | `api_response`, errors |
| [Authentication](http/authentication.md) | {%- if cookiecutter.use_jwt == "y" %}JWT{%- else %}Session{%- endif %}, password flows |
| [Permissions](http/permissions.md) | Deny-by-default |
| [Pagination](http/pagination.md) | List page shape |
| [Filtering](http/filtering.md) | Optional FilterSet |
| [Throttling](http/throttling.md) | Auth/register rates |
| [Swagger / OpenAPI](http/swagger.md) | drf-spectacular |
| [Security](http/security.md) | Secrets, DEBUG, CSRF |

### `ops/`

| Doc | Topic |
|-----|--------|
| [Settings](ops/settings.md) | Modular `config/settings/` |
{%- if cookiecutter.use_testing == "y" %}
| [Testing](ops/testing.md) | Layer tests |
{%- endif %}
| [Logging](ops/logging.md) | Handlers, request ID |
| [Migrations](ops/migrations.md) | Expand/contract |
| [Translations](ops/translations.md) | gettext msgids |
| [Code quality](ops/code-quality.md) | {%- if cookiecutter.use_code_style == "y" %}Ruff / pre-commit{%- else %}flake8 / mypy{%- endif %} |
| [Commands](ops/commands.md) | `make`, scripts |
| [Docker & production](ops/docker-and-production.md) | Compose |
{%- if cookiecutter.use_celery == "y" %}
| [Celery](ops/celery.md) | Background tasks (broker: {{cookiecutter.celery_broker}}) |
{%- endif %}
{%- if cookiecutter.use_websockets == "y" %}
| [WebSockets](ops/websockets.md) | Channels |
{%- endif %}
| [Enterprise extensions](ops/enterprise-extensions.md) | Not shipped — only if asked |
