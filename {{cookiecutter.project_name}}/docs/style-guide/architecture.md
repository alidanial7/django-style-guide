# Architecture

## Layer map

```text
HTTP request
    │
    ▼
urls (api/v1/ → app urls/)
    │
    ▼
API view (APIView + optional ApiAuthMixin)
    │  validates input via InputSerializer
    │  calls selector (read) and/or service (write)
    ▼
selector / service
    │  selector → QuerySet / model reads
    │  service → business rules + model_create / model_save / IntegrityError map
    ▼
models (+ DB constraints)
    │
    ▼
api_response / api_exception_handler
    │
    ▼
{ success, status, result, messages }
```

## Platform vs domain

| Concern | Location | Examples |
|---------|----------|----------|
| Platform | `{{cookiecutter.project_slug}}.common` | `ErrorCode`, generic `is_*`, integrity mapping, `api_response`, `model_create` |
| Domain | each app (`users`, `blogs`, …) | `UserErrorCode`, password validators, `register()`, profile selectors |
| HTTP surface | `<app>/apis/` + `api/` | Views, pagination helpers, auth mixin |
| Project wiring | `config/` | Settings slices, root URLconf, Celery, request ID |

**Do not** put domain password rules in `common`, raising validators in `errors/`, or business/permission rules in serializers beyond input shape and cross-field `validate()`.

## Built-in packages

| Package | Role |
|---------|------|
| `core` | Cross-cutting system APIs (health), shared exceptions (`ApplicationError`) |
| `common` | Reusable platform primitives (HTTP envelope, integrity, services helpers, `BaseModel`) |
| `commands` | Project management commands (`devserver`, `start_domain_app`) |
| `users` | Identity: models, auth APIs, profile, password policy |
| `api` | Top-level `/api/v1/` router, pagination helpers, `ApiAuthMixin` |
| `utils` | Shared test bases / small helpers (keep thin) |

## Request flow example (register)

1. `POST /api/v1/users/register/` → `UsersRegisterApi`
2. `UsersRegisterInputSerializer` validates shape + password validators + confirm match
3. `register(...)` service creates user (maps integrity errors) and updates profile
4. Output serializer builds payload (avatar URL{%- if cookiecutter.use_jwt == "y" %}, JWT tokens{%- endif %})
5. `api_response(..., http_status=201)` returns the success envelope

## What not to do

- Call ORM writes from views or serializers
- Put list/filter query logic in services (use selectors)
- Return raw `Response(data)` for API payloads (use `api_response`)
- Duplicate the exception handler under `api/exception_handlers.py` (legacy alias only)
- Use Django’s default `startapp` layout (use `start_domain_app`)

See also: [Domain apps](domain-apps.md), [Services](services.md), [APIs](apis.md), [Validation & errors](validation-and-errors.md).
