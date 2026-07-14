# 🤖 AGENTS.md

Instructions for coding agents working in this generated project.

## Source of truth

1. Read [`docs/style-guide/README.md`](docs/style-guide/README.md) before changing architecture.
2. Prefer existing patterns in `{{cookiecutter.project_slug}}/users/` as the reference domain app.
3. Do **not** invent a parallel layout (`views.py`, fat models, second exception handler).

## Hard rules

| Rule | Detail |
|------|--------|
| Layers | APIs glue only; **selectors** read; **services** write — see [Architecture → Layer contracts](docs/style-guide/structure/architecture.md) |
| APIs | Folders under `apis/` **mirror URL segments**; prefer `{Entity}ListCreateApiView` / `{Entity}RetrieveUpdateDestroyApiView`; action endpoints use descriptive `*ApiView` names |
| Responses | Always `api_response` / pagination helpers — envelope `{success,status,result,messages}` |
| Permissions | Default is **IsAuthenticated**; public views must set `AllowAny` |
| Validation | `is_*` + `*Validator` + domain `*ErrorCode`; uniqueness via DB + `map_integrity_error` |
| Lists | Selector (`list_<entities>`) → pagination; **no filters by default** |
| Filters | When needed: `<Entity>Filter` in `apis/<route…>/<entity>_search_filters.py`, applied **in the list view** after `list_*()` — never inside the selector / never `request` on the selector |
| Selectors | Package `selectors/`; `get_*` / `list_<entities>`; one optimized list selector (with related); second selector only for a **different job** (`list_post_ids`, …) |
| Services | Package `services/`; modules always `*_services.py` (plural) — never `*_service.py` |
| URLs | Prefer multiple modules under `urls/`: `<prefix>_url.py` per public mount (`auth_url.py`, `users_url.py`, `pos_url.py`, …) |
| Models | Class docstring `Model to declare …`; every field **both** `verbose_name=_("serial number")`-style **and** `help_text="…"`; every FK/O2O has explicit `related_name` (plural / role / `"+"`); `Meta.verbose_name(_plural)` |
| Enums | `TextChoices` / `IntegerChoices` in `<app>/enums.py` — never nested on the model |
| Keyword-only | Services/selectors use `def foo(*, …)` |
| New apps | `python manage.py start_domain_app <plural>` — never Django `startapp` |
| Strings | Prefer lowercase, space-separated gettext msgids for user-facing text (strong recommendation — see [Translations](docs/style-guide/platform/translations.md)) |
| Secrets | Never commit `.env` secrets or log tokens/passwords |

## OpenAPI

Document success payloads with `envelope_serializer(...)` from `common.http.schema` so Swagger matches the runtime envelope. Document FilterSet query params when the list accepts filters.

## Out of scope unless asked

Soft delete, multi-tenancy, full RBAC, outbox, idempotency keys — see [`docs/style-guide/structure/enterprise-extensions.md`](docs/style-guide/structure/enterprise-extensions.md).

## Quick links

- [Architecture](docs/style-guide/structure/architecture.md)
- [APIs](docs/style-guide/layers/apis.md)
- [Selectors](docs/style-guide/layers/selectors.md)
- [Enums](docs/style-guide/layers/enums.md)
- [Pagination & filtering](docs/style-guide/http/pagination-and-filtering.md)
- [Security](docs/style-guide/http/security.md)
- [Validation & errors](docs/style-guide/http/validation-and-errors.md)
- [Domain apps](docs/style-guide/structure/domain-apps.md)
