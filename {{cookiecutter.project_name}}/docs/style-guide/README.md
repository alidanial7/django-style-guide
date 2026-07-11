# Style guide

Conventions for how this codebase is structured and how new code should be written.

Inspired by the [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide): **thin views**, **fat services**, **selectors for reads**, and clear boundaries between platform (`common`) and domain apps (`users`, …).

## Principles

1. **Domain apps own business rules** — not views, not serializers beyond input shape.
2. **Selectors read; services write** — never mix the two in one function.
3. **APIs are glue** — parse input, call service/selector, return `api_response`.
4. **DB constraints are the source of truth** for uniqueness / FK / NOT NULL; validators are UX.
5. **One API envelope** for success and error (`success`, `status`, `result`, `messages`).
6. **Platform vs domain** — shared infrastructure in `common/`; app-specific codes and validators in the app.

## Index

### Structure

| Doc | Topic |
|-----|--------|
| [Architecture](architecture.md) | Layers, request flow, what lives where |
| [Project structure](project-structure.md) | Top-level folders, `config/`, package layout |
| [Domain apps](domain-apps.md) | `start_domain_app`, naming, scaffolding checklist |

### Layers (how to write code)

| Doc | Topic |
|-----|--------|
| [Models](models.md) | Models package, `BaseModel`, constraints |
| [Selectors](selectors.md) | Read queries |
| [Services](services.md) | Writes, business rules, integrity |
| [APIs & serializers](apis.md) | Views, input/output serializers, Swagger tags |
| [URLs & routing](urls.md) | Versioned API, per-app `urls/` |
| [Constants](constants.md) | Tags, static paths, app-level literals |
| [Signals](signals.md) | Mechanical side effects, `AppConfig.ready()` |

### Cross-cutting

| Doc | Topic |
|-----|--------|
| [Validation & errors](validation-and-errors.md) | `is_*`, `*Validator`, error codes, integrity mapping |
| [API response envelope](api-envelope.md) | `api_response`, exception handler shape |
| [Authentication](authentication.md) | JWT or session, password flows, endpoints |
| [Permissions](permissions.md) | `ApiAuthMixin`, DRF permissions |
| [Swagger / OpenAPI](swagger.md) | drf-spectacular, DEBUG-only UI |
| [Pagination & filtering](pagination-and-filtering.md) | Limit/offset helpers, django-filter |
| [Throttling](throttling.md) | Scoped rates for auth/register/reset |
| [Logging](logging.md) | Handlers, request ID, conventions |
| [Settings](settings.md) | Modular `config/settings/` |
| [Testing](testing.md) | pytest layout, factories |
| [Translations](translations.md) | gettext, lowercase msgids |
| [Code quality](code-quality.md) | Ruff / pre-commit / flake8 |
| [Docker & production](docker-and-production.md) | Dev infra, Compose production |
| [Commands](commands.md) | `make`, management commands, scripts |
