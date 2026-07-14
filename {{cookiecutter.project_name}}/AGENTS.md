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
| Responses | Always `api_response` / pagination helpers — envelope `{success,status,result,messages}` |
| Permissions | Default is **IsAuthenticated**; public views must set `AllowAny` |
| Validation | `is_*` + `*Validator` + domain `*ErrorCode`; uniqueness via DB + `map_integrity_error` |
| Lists | Selector (`list_<entities>`) → pagination; **no filters by default** |
| Filters | When needed: always django-filter `<Entity>Filter` on selector QS — even for 1–2 fields; never silent `filter_backends` on `APIView` |
| Selectors | `get_*` / `list_<entities>`; one optimized list selector (with related); second selector only for a **different job** (`list_post_ids`, …) |
| Models | Class docstring `Model to declare …`; every field `verbose_name=_("serial number")`-style + useful `help_text`; `Meta.verbose_name(_plural)` |
| Keyword-only | Services/selectors use `def foo(*, …)` |
| New apps | `python manage.py start_domain_app <plural>` — never Django `startapp` |
| Strings | Lowercase gettext msgids for user-facing text |
| Secrets | Never commit `.env` secrets or log tokens/passwords |

## OpenAPI

Document success payloads with `envelope_serializer(...)` from `common.http.schema` so Swagger matches the runtime envelope. Document FilterSet query params when the list accepts filters.

## Out of scope unless asked

Soft delete, multi-tenancy, full RBAC, outbox, idempotency keys — see [`docs/style-guide/structure/enterprise-extensions.md`](docs/style-guide/structure/enterprise-extensions.md).

## Quick links

- [Architecture](docs/style-guide/structure/architecture.md)
- [APIs](docs/style-guide/layers/apis.md)
- [Selectors](docs/style-guide/layers/selectors.md)
- [Pagination & filtering](docs/style-guide/http/pagination-and-filtering.md)
- [Security](docs/style-guide/http/security.md)
- [Validation & errors](docs/style-guide/http/validation-and-errors.md)
- [Domain apps](docs/style-guide/structure/domain-apps.md)
