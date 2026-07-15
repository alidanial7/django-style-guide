# Style guide

Conventions for how this codebase is structured and how new code should be written.

Inspired by the [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide): **thin views**, **fat services**, **selectors for reads**, and clear boundaries between platform (`common`) and domain apps (`users`, …).

Agents: start at [`AGENTS.md`](../../AGENTS.md) then this index.

## Layout

```text
docs/style-guide/
├── README.md      # this index
├── overview/      # big picture: architecture, folders, scaffolding
├── domain/        # how to build app code (models → APIs, validation, errors)
├── http/          # request/response contract (envelope, auth, pagination, …)
└── ops/           # how to run & ship (settings, tests, docker, celery, …)
```

**How to read:** start with `overview/`, then `domain/` for day-to-day code, then `http/` for the API contract, then `ops/` when you need tooling or deploy.

## Principles

1. **Domain apps own business rules** — not views, not serializers beyond input shape.
2. **Selectors read; services write** — never mix the two in one function.
3. **APIs are glue** — InputSerializer → service(`data=` TypedDict) / selector → `api_response`.
4. **DB constraints are the source of truth** for uniqueness / FK / NOT NULL; validators are UX.
5. **One API envelope** for success and error (`success`, `status`, `result`, `messages`).
6. **Platform vs domain** — shared infrastructure in `common/`; app-specific codes and validators in the app.
7. **Deny by default** — APIs are `IsAuthenticated` unless a view sets `AllowAny`.
8. **Lists** — selector + pagination by default; filters live in `apis/` as `*_search_filters.py` (FilterSet applied in the list view after `list_*()`).
9. **TypedDict** — write services take `data: Create*Data` / `Update*Data`; no dataclass DTOs; serializers never `save()`.

## Index

### `overview/` — start here

| Doc | Topic |
|-----|--------|
| [Architecture](overview/architecture.md) | Layers, request flow, **layer contracts**, what lives where |
| [Project structure](overview/project-structure.md) | Top-level folders, `config/`, package layout |
| [Domain apps](overview/domain-apps.md) | `start_domain_app`, naming, scaffolding checklist |

### `domain/` — writing app code

| Doc | Topic |
|-----|--------|
| [Models](domain/models.md) | Models package, `BaseModel`, labels, `related_name`, constraints |
| [Enums](domain/enums.md) | `TextChoices` / `IntegerChoices` in `enums.py` |
| [Selectors](domain/selectors.md) | Read queries, naming |
| [Types](domain/types.md) | TypedDict service inputs (no dataclass DTOs) |
| [Services](domain/services.md) | Writes, business rules, integrity |
| [APIs & serializers](domain/apis.md) | Route-mirrored `apis/` folders, views, serializers |
| [URLs & routing](domain/urls.md) | Versioned API, per-app `urls/` |
| [Validation](domain/validation.md) | Pure `is_*` checks and raising `*Validator` classes |
| [Errors](domain/errors.md) | `ErrorCode` / domain codes, integrity mapping |
| [Constants](domain/constants.md) | Tags, static paths, app-level literals |
| [Signals](domain/signals.md) | Mechanical side effects, `AppConfig.ready()` |

### `http/` — API contract

| Doc | Topic |
|-----|--------|
| [API response envelope](http/api-envelope.md) | `api_response`, `envelope_serializer`, error shape |
| [Authentication](http/authentication.md) | JWT or session, password flows, endpoints |
| [Permissions](http/permissions.md) | Deny-by-default, `AllowAny`, `ApiAuthMixin` |
| [Pagination](http/pagination.md) | Limit/offset, cursor, page shape inside the envelope |
| [Filtering](http/filtering.md) | Optional django-filter `FilterSet` under `apis/` |
| [Throttling](http/throttling.md) | Scoped rates for auth/register/reset |
| [Swagger / OpenAPI](http/swagger.md) | drf-spectacular, envelope in schema |
| [Security](http/security.md) | Secrets, DEBUG, CSRF, production hardening |

### `ops/` — run, test, ship

| Doc | Topic |
|-----|--------|
| [Settings](ops/settings.md) | Modular `config/settings/` |
| [Testing](ops/testing.md) | selectors = queries; services = logic; APIs = integration |
| [Logging](ops/logging.md) | Handlers, request ID, conventions |
| [Migrations](ops/migrations.md) | Expand/contract, zero-downtime habits |
| [Translations](ops/translations.md) | gettext; prefer lowercase + space-separated msgids |
| [Code quality](ops/code-quality.md) | Ruff / pre-commit / flake8 |
| [Commands](ops/commands.md) | `make`, management commands, scripts |
| [Docker & production](ops/docker-and-production.md) | Dev infra, Compose production |
| [Celery](ops/celery.md) | Background tasks (if enabled) |
| [WebSockets](ops/websockets.md) | Channels (if enabled) |
| [Enterprise extensions](ops/enterprise-extensions.md) | Soft delete, RBAC, multi-tenant, … (not shipped) |
