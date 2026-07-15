# 🤖 AGENTS.md

Instructions for coding agents working in this generated project.

## Source of truth

1. Read [`docs/style-guide/README.md`](docs/style-guide/README.md) before changing architecture.
2. Prefer existing patterns in `{{cookiecutter.project_slug}}/users/` as the reference domain app.
3. Do **not** invent a parallel layout (`views.py`, fat models, second exception handler).

## Hard rules

| Rule | Detail |
|------|--------|
| Layers | APIs glue only; **serializers** = HTTP; **TypedDict** types service `data=`; **selectors** read; **services** write — see [Architecture](docs/style-guide/overview/architecture.md) / [Types](docs/style-guide/domain/types.md) |
| APIs | Folders under `apis/` **mirror URL segments**; prefer `{Entity}ListCreateApiView` / `{Entity}RetrieveUpdateDestroyApiView`; action endpoints use descriptive `*ApiView` names |
| Responses | Always `api_response` / pagination helpers — envelope `{success,status,result,messages}` |
| Permissions | Default is **IsAuthenticated**; public views must set `AllowAny` |
| Validation | `is_*` + `*Validator` + domain `*ErrorCode`; uniqueness via DB + `map_integrity_error` |
| Lists | Selector (`list_<entities>`) → pagination; **no filters by default** |
| Filters | When needed: `<Entity>Filter` in `apis/<route…>/<entity>_search_filters.py`, applied **in the list view** after `list_*()` — never inside the selector / never `request` on the selector |
| Selectors | Package `selectors/`; `get_*` / `list_<entities>`; one optimized list selector (with related); second selector only for a **different job** (`list_post_ids`, …) |
| Services | Package `services/`; modules always `*_services.py` (plural) — never `*_service.py`; write inputs are **TypedDict** (`data: Create*Data`), never untyped `dict` / dataclass DTOs |
| Types | `<app>/types.py` with `TypedDict` (`Create*Data` / `Update*Data`, `total=False` for PATCH) — see [Types](docs/style-guide/domain/types.md) |
| URLs | Prefer multiple modules under `urls/`: `<prefix>_url.py` per public mount (`auth_url.py`, `users_url.py`, `pos_url.py`, …) |
| Models | Class docstring `Model to declare …`; every field **both** `verbose_name=_("serial number")`-style **and** `help_text="…"`; every FK/O2O has explicit `related_name` (plural / role / `"+"`); `Meta.verbose_name(_plural)` |
| Enums | `TextChoices` / `IntegerChoices` in `<app>/enums.py` — never nested on the model |
| Keyword-only | Services/selectors use `def foo(*, …)` |
| Service inputs | `service(..., data=serializer.validated_data)` typed as TypedDict; PATCH uses `"field" in data`; no `serializer.save()` / no dataclass DTOs |
| Tests | Selectors = query correctness; services = business logic (TypedDict literals); APIs = integration — see [Testing](docs/style-guide/ops/testing.md) |
| New apps | `python manage.py start_domain_app <plural>` — never Django `startapp` |
| Strings | Prefer lowercase, space-separated gettext msgids for user-facing text (strong recommendation — see [Translations](docs/style-guide/ops/translations.md)) |
| Secrets | Never commit `.env` secrets or log tokens/passwords |

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
