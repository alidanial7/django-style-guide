# 🤖 AGENTS.md

Always-on cheat sheet. **Do not** open `docs/style-guide/` for routine edits that fit a row below. Open a linked page only when that row is not enough to implement correctly, or when changing a convention.

## Source of truth

1. Read [`docs/style-guide/README.md`](docs/style-guide/README.md) before changing architecture.
2. Prefer existing patterns in `{{cookiecutter.project_slug}}/users/` as the reference domain app.
3. Do **not** invent a parallel layout (`views.py`, fat models, second exception handler).
4. Convention change → update the style-guide page in the **same change**; update this sheet only if the one-line Hard rule changes.

## Hard rules

| Rule | One-liner | Open only if needed |
|------|-----------|---------------------|
| Layers | APIs glue only; serializers = HTTP; TypedDict = service `data=`; selectors read; services write | [Architecture](docs/style-guide/overview/architecture.md) · [Types](docs/style-guide/domain/types.md) |
| APIs | `apis/` mirrors URL segments; `{Entity}ListCreate` / `RetrieveUpdateDestroy`; actions → `*ApiView` | [APIs](docs/style-guide/domain/apis.md) |
| Scoped surfaces | `/api/v1/<scope>/` strictly mirrors to `apis/<scope>/<resource>/`; leaf `tests/` in BOTH collection & `id/`; dedicated `<Scope>*` serializers; isolated `<scope>_<app>_url.py` | [APIs](docs/style-guide/domain/apis.md#client--surface-scoped-apis-eg-apiv1site) |
| Responses | Always `api_response` / pagination helpers — `{success,status,result,messages}` | [Envelope](docs/style-guide/http/api-envelope.md) |
| Permissions | Default **IsAuthenticated**; public views must set `AllowAny` | [Permissions](docs/style-guide/http/permissions.md) |
| Validation | `is_*` + `*Validator` + domain `*ErrorCode`; uniqueness = DB + `map_integrity_error` | [Validation](docs/style-guide/domain/validation.md) · [Errors](docs/style-guide/domain/errors.md) |
| Lists | `list_<entities>` → pagination; **no filters by default** | [Pagination](docs/style-guide/http/pagination.md) |
| Filters | `<Entity>Filter` in `apis/…/*_search_filters.py`; apply in list view after `list_*()` — never inside selector | [Filtering](docs/style-guide/http/filtering.md) |
| Selectors | Package `selectors/`; `get_*` / `list_<entities>`; one optimized list selector; second selector only for a different job | [Selectors](docs/style-guide/domain/selectors.md) |
| Services | `*_services.py`; `data=` TypedDict; `model_create` / `model_update` / `model_save`; no `serializer.save()` / no dataclass DTOs | [Services](docs/style-guide/domain/services.md) |
| Types | `<app>/types.py` — `Create*Data` / `Update*Data` (`total=False` for PATCH) | [Types](docs/style-guide/domain/types.md) |
| Models | `BaseModel` UUID PK; docstring `Model to declare …`; every field `verbose_name` + `help_text`; explicit `related_name` | [Models](docs/style-guide/domain/models.md) |
| URLs | `urls/<prefix>_url.py`; plural resource nouns (`/users/<id>/` not `/user/<id>/`); path ids `<uuid:entity_id>` | [URLs](docs/style-guide/domain/urls.md) |
| Enums | `TextChoices` / `IntegerChoices` in `<app>/enums.py` — never nested on the model | [Enums](docs/style-guide/domain/enums.md) |
| Keyword-only | Services/selectors use `def foo(*, …)` | — |
| Tests | Selectors = query correctness; services = business logic (TypedDict literals); APIs = integration | [Testing](docs/style-guide/ops/testing.md) |
| New apps | `python manage.py start_domain_app <plural>` — never Django `startapp` | [Domain apps](docs/style-guide/overview/domain-apps.md) |
| Strings | Prefer lowercase, space-separated gettext msgids for user-facing text | [Translations](docs/style-guide/ops/translations.md) |
| Docstrings | Class docstring + `@extend_schema`; if Google style used, types in `(Type):` and `Raises:` must match signature/body | [Code quality](docs/style-guide/ops/code-quality.md) |
| Model Admin Sync | Whenever a model is created or modified, its admin MUST be updated in `<app>/admin.py` (`ModelAdmin`, `list_display`, `list_filter`, `search_fields`, `readonly_fields`) | — |
| Infra alert | Changes to env vars, Celery/RabbitMQ/Redis/DB, Dockerfile, ports, entrypoints -> MUST alert developer that deployment/infra needs updating | — |
| Secrets | Never commit `.env` secrets or log tokens/passwords | [Security](docs/style-guide/http/security.md) |

## Git & Commits Policy

- **NEVER** run `git commit` or create git commits automatically. The user will always review changes and commit manually.
- **NEVER** run `git push` or push commits to any remote repository automatically.
- Always leave committing and pushing to the developer across all workflows.
- You may inspect `git status` or `git diff` for verification, but never execute `git commit` or `git push`.

## Browser Subagent Policy

- **NEVER** launch `browser_subagent` or open a browser automatically without the user's explicit command/request.

## Infrastructure Awareness & Developer Alerts

Whenever any change in this codebase impacts runtime dependencies, services, or deployment configuration (e.g., new/changed environment variables, Celery queues/workers, Redis DB segregation, RabbitMQ, Dockerfiles, entrypoints, healthchecks, ports, volumes):
- **MANDATORY**: You **MUST** include an explicit, dedicated section in your final response titled:
  `### ⚠️ Infrastructure & Deployment Action Required`
  Detailing:
  1. Any new or changed environment variables (with sensible production defaults).
  2. Any newly required external services, brokers, or workers.
  3. Any changes to Dockerfiles, entrypoints, ports, volumes, or healthchecks.
  4. The exact updates needed in deployment files (`docker-compose.yml`, `.env.example`, `.env`, reverse proxy configs).

## Scoped Surface APIs & URL Mirroring Policy

When building or updating endpoints under client-scoped prefixes (`/api/v1/<scope>/...` e.g., `/api/v1/site/...`, `/api/v1/admin/...`):
1. **Directory Mirroring**: Folder structure under `apis/` MUST directly mirror the URL segments:
   - Collection leaf: `apis/<scope>/<resource>/` (e.g. `apis/site/contact_infos/`).
   - Detail leaf with param: `apis/<scope>/<resource>/id/`.
   - NEVER put scoped endpoints in the root of `apis/`.
2. **Co-located Leaf Tests**:
   - Every single route leaf MUST have its own `tests/` directory right next to its `*_apis.py` and `*_serializers.py`.
   - Collection tests: `apis/<scope>/<resource>/tests/test_<scope>_<resource>_apis.py`.
   - Param detail tests: `apis/<scope>/<resource>/id/tests/test_<scope>_<resource>_id_apis.py`.
   - NEVER aggregate detail tests into a single collection `tests/` folder.
3. **Dedicated Scoped Serializers & Component Names**:
   - Serializers for client surfaces must be explicitly declared (never directly re-exported from internal APIs).
   - Use `@extend_schema_serializer(component_name="<Scope><Entity>...")` to guarantee zero typing conflicts in generated client SDKs.
4. **Isolated App URL Modules**:
   - Scope-specific routes for each domain app must reside in `urls/<scope>_<app>_url.py` and be mounted into `api/<scope>_urls.py`.

## OpenAPI

Document success payloads with `envelope_serializer(...)` from `common.http.schema` so Swagger matches the runtime envelope. Document FilterSet query params when the list accepts filters.

## Out of scope unless asked

Soft delete, multi-tenancy, full RBAC, outbox, idempotency keys — see [`docs/style-guide/ops/enterprise-extensions.md`](docs/style-guide/ops/enterprise-extensions.md).

## Quick links

- [Architecture](docs/style-guide/overview/architecture.md)
- [APIs](docs/style-guide/domain/apis.md)
- [Types](docs/style-guide/domain/types.md)
- [Selectors](docs/style-guide/domain/selectors.md)
- [Enums](docs/style-guide/domain/enums.md)
- [Pagination](docs/style-guide/http/pagination.md)
- [Filtering](docs/style-guide/http/filtering.md)
- [Security](docs/style-guide/http/security.md)
- [Validation](docs/style-guide/domain/validation.md)
- [Errors](docs/style-guide/domain/errors.md)
- [Domain apps](docs/style-guide/overview/domain-apps.md)
