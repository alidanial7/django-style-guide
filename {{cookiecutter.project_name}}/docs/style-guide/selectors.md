# Selectors

Selectors are **read-only** query functions. They fetch and shape data for APIs and services. They must not create, update, or delete rows (except `get_or_create` when it is purely ensuring a derived read model exists — prefer documenting that case clearly, as in `get_profile`).

## Location & naming

```text
<app>/selector/
├── __init__.py
└── <app>_selectors.py    # e.g. users_selectors.py
```

Name functions with a clear verb: `get_profile`, `list_published_posts`, `get_avatar_url`.

## Style

- Keyword-only arguments (`*`) for clarity at call sites.
- Return models, querysets, or plain values — not Response objects.
- Prefer `select_related` / `prefetch_related` here, not in views.
- Reuse selectors from services when a write path also needs a read (e.g. load profile then update).

## Example

```python
# users/selector/users_selectors.py
def get_profile(*, user: BaseUser) -> Profile:
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def get_avatar_url(*, profile: Profile, request: HttpRequest | None = None) -> str:
    ...
```

Called from an API:

```python
profile = get_profile(user=request.user)
return api_response(data=UsersProfileOutputSerializer(profile, context={"request": request}).data)
```

## Tests

Place selector tests under `selector/tests/`. Assert query behavior and returned shapes; avoid testing HTTP.

## Anti-patterns

- Putting filter/list logic only inside `APIView.get` with inline ORM
- Writing to the database inside a selector without a strong reason
- Returning DRF serializers from selectors (serialize in the API layer)
