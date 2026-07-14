# Style guide

Conventions for how this codebase is structured and how new code should be written.

Inspired by the [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide): **thin views**, **fat services**, **selectors for reads**, and clear boundaries between platform (`common`) and domain apps (`users`, …).

Agents: start at [`AGENTS.md`](../../AGENTS.md) then this index.

## Layout

```text
docs/style-guide/
├── README.md                 # this index
├── structure/                # architecture, folders, scaffolding
├── layers/                   # models → selectors → services → APIs → urls
├── http/                     # envelope, auth, security, OpenAPI, filters
└── platform/                 # settings, logging, docker, tests, celery, …
```

## Principles

1. **Domain apps own business rules** — not views, not serializers beyond input shape.
2. **Selectors read; services write** — never mix the two in one function.
3. **APIs are glue** — parse input, call service/selector, return `api_response`.
4. **DB constraints are the source of truth** for uniqueness / FK / NOT NULL; validators are UX.
5. **One API envelope** for success and error (`success`, `status`, `result`, `messages`).
6. **Platform vs domain** — shared infrastructure in `common/`; app-specific codes and validators in the app.
7. **Deny by default** — APIs are `IsAuthenticated` unless a view sets `AllowAny`.
8. **Lists** — selector + pagination by default; filters live in `apis/` as `*_search_filters.py` (FilterSet applied in the list view after `list_*()`).

## Index

### `structure/`

| Doc | Topic |
|-----|--------|
| [Architecture](structure/architecture.md) | Layers, request flow, **layer contracts**, what lives where |
| [Project structure](structure/project-structure.md) | Top-level folders, `config/`, package layout |
| [Domain apps](structure/domain-apps.md) | `start_domain_app`, naming, scaffolding checklist |
| [Enterprise extensions](structure/enterprise-extensions.md) | Soft delete, RBAC, multi-tenant, … (not shipped) |

### `layers/`

| Doc | Topic |
|-----|--------|
| [Models](layers/models.md) | Models package, `BaseModel`, labels, `related_name`, constraints |
| [Enums](layers/enums.md) | `TextChoices` / `IntegerChoices` in `enums.py` |
| [Selectors](layers/selectors.md) | Read queries, naming |
| [Services](layers/services.md) | Writes, business rules, integrity |
| [APIs & serializers](layers/apis.md) | Route-mirrored `apis/` folders, `*ListCreateApiView` / `*RetrieveUpdateDestroyApiView`, serializers |
| [URLs & routing](layers/urls.md) | Versioned API, per-app `urls/` |
| [Constants](layers/constants.md) | Tags, static paths, app-level literals |
| [Signals](layers/signals.md) | Mechanical side effects, `AppConfig.ready()` |

### `http/`

| Doc | Topic |
|-----|--------|
| [Validation & errors](http/validation-and-errors.md) | `is_*`, `*Validator`, error codes, integrity mapping |
| [API response envelope](http/api-envelope.md) | `api_response`, `envelope_serializer`, error shape |
| [Authentication](http/authentication.md) | JWT or session, password flows, endpoints |
| [Permissions](http/permissions.md) | Deny-by-default, `AllowAny`, `ApiAuthMixin` |
| [Security](http/security.md) | Secrets, DEBUG, CSRF, production hardening |
| [Swagger / OpenAPI](http/swagger.md) | drf-spectacular, envelope in schema |
| [Pagination & filtering](http/pagination-and-filtering.md) | Limit/offset, cursor, FilterSet under `apis/` |
| [Throttling](http/throttling.md) | Scoped rates for auth/register/reset |

### `platform/`

| Doc | Topic |
|-----|--------|
| [Logging](platform/logging.md) | Handlers, request ID, conventions |
| [Migrations](platform/migrations.md) | Expand/contract, zero-downtime habits |
| [Settings](platform/settings.md) | Modular `config/settings/` |
| [Testing](platform/testing.md) | pytest layout, factories |
| [Translations](platform/translations.md) | gettext; prefer lowercase + space-separated msgids |
| [Code quality](platform/code-quality.md) | Ruff / pre-commit / flake8 |
| [Celery](platform/celery.md) | Background tasks (if enabled) |
| [WebSockets](platform/websockets.md) | Channels (if enabled) |
| [Docker & production](platform/docker-and-production.md) | Dev infra, Compose production |
| [Commands](platform/commands.md) | `make`, management commands, scripts |
