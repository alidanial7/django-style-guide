# API response envelope

Success and error responses share one outer shape. Use `api_response(...)` from `common.http` in views — do not return raw `Response(data)` for API payloads.

## Success

```json
{
  "success": true,
  "status": 200,
  "result": { "email": "a@example.com" },
  "messages": {}
}
```

Created by:

```python
from {{cookiecutter.project_slug}}.common.http import api_response

return api_response(data=payload, http_status=status.HTTP_200_OK)
```

If `data` is `None`, `result` becomes `{}`.

## Error

```json
{
  "success": false,
  "status": 400,
  "result": [],
  "messages": {
    "email": [
      { "message": "email already exists.", "code": "unique" }
    ],
    "confirm_password": [
      { "message": "confirm password is not equal to password", "code": "password_mismatch" }
    ]
  }
}
```

Each error field maps to a list of `{ "message", "code" }` objects.

| Case | Code behavior |
|------|----------------|
| Raiser omitted `code=` | Fallback `"invalid"` (`ErrorCode.INVALID`) |
| Unexpected server error | `"server_error"` — internals never leaked |
| `ApplicationError` | `"application_error"` on `non_field_errors` (+ optional `extra`) |

## Wiring

Configured in `config/settings/drf.py`:

```python
"EXCEPTION_HANDLER": "{{cookiecutter.project_slug}}.common.http.exception_handler.api_exception_handler"
```

`api/exception_handlers.py` is a **thin legacy alias** only — do not add a second implementation.

## Handler behavior (summary)

`api_exception_handler`:

1. Converts Django `ValidationError` → DRF validation error
2. Maps `Http404` / Django `PermissionDenied` to DRF equivalents
3. Handles `ApplicationError` with a 400 envelope
4. Normalizes DRF errors into `messages`
5. For unhandled exceptions in a DRF view: logs with `logger.exception` and returns a generic 500 envelope

## Pagination

Paginated list endpoints still use the success envelope; `result` contains `limit`, `offset`, `count`, `next`, `previous`, `results`. See [Pagination & filtering](pagination-and-filtering.md).
