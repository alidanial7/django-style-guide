# Pagination & filtering

## Pagination helpers

Location: `{{cookiecutter.project_slug}}/api/pagination.py`.

| Helper | Use |
|--------|-----|
| `get_paginated_response(...)` | Paginate queryset + serialize without request context |
| `get_paginated_response_context(...)` | Same, but passes `context={"request": request}` to the serializer |
| `LimitOffsetPagination` | `default_limit=10`, `max_limit=50`; wraps data in `api_response` |

Paginated success `result` shape:

```json
{
  "limit": 10,
  "offset": 0,
  "count": 42,
  "next": "...",
  "previous": null,
  "results": [ ... ]
}
```

Example:

```python
from {{cookiecutter.project_slug}}.api.pagination import LimitOffsetPagination, get_paginated_response_context

class PostListApi(ApiAuthMixin, APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 20

    def get(self, request):
        qs = list_posts()  # selector
        return get_paginated_response_context(
            pagination_class=self.Pagination,
            serializer_class=PostOutputSerializer,
            queryset=qs,
            request=request,
            view=self,
        )
```

If pagination returns `None` (edge case), helpers fall back to `api_response(data=serializer.data)` for the full queryset.

## Filtering

`DEFAULT_FILTER_BACKENDS` includes `DjangoFilterBackend` (`config/settings/drf.py`).

Prefer:

1. Selector accepts explicit filter kwargs / a small filter dataclass, **or**
2. A `django_filters.FilterSet` used from the view, with the filtered queryset still obtained in a clear way

Keep heavy query construction in **selectors**, not in the view body.

## Ordering / search

Add DRF backends (`OrderingFilter`, `SearchFilter`) per-view when needed; document query params in `@extend_schema`.
