# 🤖 AGENTS.md

Instructions for coding agents working in this generated project.

## Source of truth

1. Read [`docs/style-guide/README.md`](docs/style-guide/README.md) before changing architecture.
2. Prefer existing patterns in `{{cookiecutter.project_slug}}/users/` as the reference domain app.
3. Do **not** invent a parallel layout (`views.py`, fat models, second exception handler).

## Hard rules

| Rule | Detail |
|------|--------|
| Layers | APIs glue only; **selectors** read; **services** write |
| Responses | Always `api_response` / pagination helpers — envelope `{success,status,result,messages}` |
| Permissions | Default is **IsAuthenticated**; public views must set `AllowAny` |
| Validation | `is_*` + `*Validator` + domain `*ErrorCode`; uniqueness via DB + `map_integrity_error` |
| New apps | `python manage.py start_domain_app <plural>` — never Django `startapp` |
| Strings | Lowercase gettext msgids for user-facing text |
| Secrets | Never commit `.env` secrets or log tokens/passwords |

## OpenAPI

Document success payloads with `envelope_serializer(...)` from `common.http.schema` so Swagger matches the runtime envelope.

## Out of scope unless asked

Soft delete, multi-tenancy, full RBAC, outbox, idempotency keys — see [`docs/style-guide/enterprise-extensions.md`](docs/style-guide/enterprise-extensions.md).

## Quick links

- [Architecture](docs/style-guide/architecture.md)
- [Security](docs/style-guide/security.md)
- [Validation & errors](docs/style-guide/validation-and-errors.md)
- [APIs](docs/style-guide/apis.md)
- [Domain apps](docs/style-guide/domain-apps.md)
