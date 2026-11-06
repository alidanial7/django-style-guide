# Agents

Minimal always-on index. **Do not** bulk-read `docs/style-guide/`. Cursor loads matching `.cursor/rules/*.mdc` by glob; open **one** style-guide page only when a rule is not enough to implement correctly.

## Source of truth

1. Patterns in `{{cookiecutter.project_slug}}/users/` — reference domain app.
2. `.cursor/rules/` — actionable rules (prefer these).
3. `docs/style-guide/` — deep detail / convention changes only.
4. Convention change → update the matching style-guide page in the **same** change.

## Hard don'ts

- Invent parallel layouts (`views.py`, fat models, second exception handler).
- `git commit` / `git push` (user commits).
- Open a browser unless the user asks.
- Commit `.env` secrets or log tokens/passwords.

## Hard dos

- New apps: `python manage.py start_domain_app <plural>` — never `startapp`.
- APIs glue only; serializers = HTTP; TypedDict = service `data=`; selectors read; services write.
- Responses: `api_response` / pagination helpers — `{success,status,result,messages}`.
- Default permission **IsAuthenticated**; public views set `AllowAny`.
- Services/selectors: keyword-only `def foo(*, …)`.
- Writes via `model_create` / `model_update` / `model_save` / `model_delete`.
- Model/admin stay in sync (`admin.py` when models change).
- OpenAPI: Input/Output split; `envelope_serializer` / `paginated_envelope_serializer`; `request=None` for bodiless POST; document DELETE responses; register enums in `ENUM_NAME_OVERRIDES`.
- Schema/data needing seeds → update `seed_demo_data` / `initial_system` (ask first).
{%- if cookiecutter.use_uuid_pk == "y" %}
- Domain models inherit `BaseModel` (UUID PK); URL ids `<uuid:entity_id>`.
{%- else %}
- Domain models inherit `BaseModel` (timestamps; default `BigAutoField`); URL ids `<int:entity_id>`.
{%- endif %}
{%- if cookiecutter.user_login_field == "username" %}
- Auth login field: **username** (`USERNAME_FIELD`); email remains unique for reset/notify.
{%- else %}
- Auth login field: **email** (`USERNAME_FIELD`).
{%- endif %}
{%- if cookiecutter.use_file_manager == "y" %}
- Uploads: `ManagedFile` only — no ad-hoc `FileField` / `ImageField` on domain models.
{%- endif %}

## Read only when needed

| Working on | Rule (auto via glob) | Deep doc if stuck |
|------------|----------------------|-------------------|
| Layers / feature flow | `layers` | [Architecture](docs/style-guide/overview/architecture.md) |
| `apis/`, serializers, URLs | `apis` | [APIs](docs/style-guide/domain/apis.md) · [URLs](docs/style-guide/domain/urls.md) |
| models | `models` | [Models](docs/style-guide/domain/models.md) |
| services / selectors / types | `services-selectors` | [Services](docs/style-guide/domain/services.md) · [Selectors](docs/style-guide/domain/selectors.md) · [Types](docs/style-guide/domain/types.md) |
| envelope / permissions / OpenAPI | `http-contract` | [Envelope](docs/style-guide/http/api-envelope.md) · [Permissions](docs/style-guide/http/permissions.md) · [Swagger](docs/style-guide/http/swagger.md) |
| auth / users auth APIs | `auth` | [Authentication](docs/style-guide/http/authentication.md) |
{%- if cookiecutter.use_file_manager == "y" %}
| file uploads / `ManagedFile` | `file-manager` | [File manager](docs/style-guide/domain/file-manager.md) |
{%- endif %}
{%- if cookiecutter.use_portal_permissions == "y" %}
| portal gates | `portal-permissions` | [Permissions](docs/style-guide/http/permissions.md) |
{%- endif %}
{%- if cookiecutter.use_unfold_admin == "y" %}
| Unfold admin | `unfold-admin` | [Admin / Unfold](docs/style-guide/ops/admin-unfold.md) |
{%- endif %}
{%- if cookiecutter.use_testing == "y" %}
| tests | `testing` | [Testing](docs/style-guide/ops/testing.md) |
{%- endif %}
{%- if cookiecutter.use_celery == "y" %}
| Celery / tasks | `celery` | [Celery](docs/style-guide/ops/celery.md) |
{%- endif %}
{%- if cookiecutter.use_websockets == "y" %}
| Channels / WS | `websockets` | [WebSockets](docs/style-guide/ops/websockets.md) |
{%- endif %}
| Docker / compose / `.env` / entrypoints | `infra` | [Docker](docs/style-guide/ops/docker-and-production.md) |
{%- if cookiecutter.use_code_style == "y" %}
| lint / pre-commit | `code-quality` | [Code quality](docs/style-guide/ops/code-quality.md) |
{%- endif %}
{%- if cookiecutter.use_sentry == "y" %}
| Sentry | `sentry` | [Settings](docs/style-guide/ops/settings.md) |
{%- endif %}
{%- if cookiecutter.use_pgadmin == "y" %}
| pgAdmin (dev) | `pgadmin` | [Docker](docs/style-guide/ops/docker-and-production.md) |
{%- endif %}
| New domain app scaffold | — | [Domain apps](docs/style-guide/overview/domain-apps.md) |
| Commands / seeds | — | [Commands](docs/style-guide/ops/commands.md) |

## Infra changes

If env vars, brokers, Dockerfiles, ports, entrypoints, or compose change → end the reply with:

`### ⚠️ Infrastructure & Deployment Action Required`

List: new/changed env vars, services/workers, Docker/entrypoint/port/volume changes, exact files to update (`.env.example`, compose, proxy){% if cookiecutter.infra_repo_name %} — and mirror into **`{{cookiecutter.infra_repo_name}}`** (may not be cloned locally){% endif %}.

## Out of scope unless asked

Soft delete, multi-tenancy, full RBAC, outbox, idempotency — [enterprise-extensions](docs/style-guide/ops/enterprise-extensions.md).
