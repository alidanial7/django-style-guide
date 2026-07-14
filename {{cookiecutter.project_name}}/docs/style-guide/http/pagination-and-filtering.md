# 📄 Pagination & filtering

> How list endpoints return pages inside the [API envelope](api-envelope.md). Filters are **off by default**; when needed, a **django-filter `FilterSet`** lives under **`apis/`** as `*_search_filters.py` and is applied **in the list view** after the selector returns the base queryset.
>
> Helpers live in `{{cookiecutter.project_slug}}/api/pagination.py`.

---

## 🎯 Why custom helpers?

DRF’s default pagination response is a bare object (`count`, `next`, `results`, …). This project wraps **everything** in `{ success, status, result, messages }`, so pagination subclasses `get_paginated_response` to put the page metadata **inside `result`**.

```mermaid
flowchart LR
    QS[QuerySet from selector] --> PAG[LimitOffsetPagination]
    PAG --> SER[OutputSerializer many=True]
    SER --> ENV["api_response → result = {limit, offset, count, next, previous, results}"]
```

---

## 📦 Paginated success shape

```json
{
  "success": true,
  "status": 200,
  "result": {
    "limit": 10,
    "offset": 0,
    "count": 42,
    "next": "http://localhost:8000/api/v1/blogs/posts/?limit=10&offset=10",
    "previous": null,
    "results": [
      { "id": 1, "title": "…" }
    ]
  },
  "messages": {}
}
```

| Field | Meaning |
|-------|---------|
| `limit` | Page size used for this response |
| `offset` | Starting index |
| `count` | Total rows matching the queryset (before slice) |
| `next` / `previous` | Absolute URLs or `null` |
| `results` | Serialized page items |

Frontends can build their own pager from `limit` / `offset` / `count` without parsing Link headers.

---

## 🧱 `LimitOffsetPagination`

```python
# api/pagination.py
class LimitOffsetPagination(_LimitOffsetPagination):
    default_limit = 10
    max_limit = 50
```

| Setting | Default | Notes |
|---------|---------|-------|
| `default_limit` | `10` | Used when client omits `limit` |
| `max_limit` | `50` | Caps abusive `?limit=100000` |

Query params (DRF limit/offset style):

```http
GET /api/v1/blogs/posts/?limit=20&offset=40
```

### Per-view overrides

```python
class PostListCreateApiView(ApiAuthMixin, APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 20
        max_limit = 100
```

---

## 📍 `CursorPagination` (large / high-churn lists)

```python
from {{cookiecutter.project_slug}}.api.pagination import CursorPagination, get_paginated_response_context

class PostFeedListApiView(ApiAuthMixin, APIView):
    class Pagination(CursorPagination):
        page_size = 20
        ordering = "-created_at"

    def get(self, request):
        qs = list_posts()
        return get_paginated_response_context(
            pagination_class=self.Pagination,
            serializer_class=PostOutputSerializer,
            queryset=qs,
            request=request,
            view=self,
        )
```

| Prefer limit/offset when | Prefer cursor when |
|--------------------------|--------------------|
| Admin tables, small catalogs, need total `count` | Feeds, event streams, rows inserted while paging |
| Clients build page numbers from `offset` | Clients only follow `next` / `previous` |

Cursor `result` shape (inside the envelope): `{ "next", "previous", "results" }` — no global `count`.

Default ordering uses `-created_at` (works with `BaseModel`). Override `ordering` for your model.

---

## 🛠️ Helper functions

| Helper | Serializer context | When to use |
|--------|-------------------|-------------|
| `get_paginated_response(...)` | none | Items need no `request` (no absolute media URLs) |
| `get_paginated_response_context(...)` | `{"request": request}` | Avatars, absolute links, anything using `request.build_absolute_uri` |

Both:

1. Instantiate your pagination class
2. `paginate_queryset(...)`
3. Serialize the page with `many=True`
4. Return `paginator.get_paginated_response(...)` → envelope

If pagination returns `None` (unusual with these settings), helpers fall back to `api_response(data=serializer.data)` for the full queryset.

### Full example

- **No query filters:** selector → pagination (see Filtering → default).
- **With filters:** selector returns optimized base QS → API applies `FilterSet` from `*_search_filters.py` → pagination / serialize.

**Never** `Model.objects.filter(...)` or `[:10]` in the view for the base list. **Never** pass `request` into a selector. Auth / ownership scoping that belongs in the read layer still lives in the selector (e.g. `for_user`); client query-string FilterSets live in `apis/`.

---

## 🔎 Filtering (django-filter under **`apis/`**)

### Project rules

| Rule | Detail |
|------|--------|
| Default | **Nothing is filtered.** List = selector + pagination only |
| When you need filters | Always use a **`django_filters.FilterSet`**, even for 1–2 fields |
| Where it lives | Next to the list API leaf: `apis/<route…>/<entity>_search_filters.py` |
| Applied where | **In the API view** after `list_*()` |
| Selector role | Optimized base QS only (`select_related` / `prefetch` / domain scoping) — **no** `query_params=` |
| Auto backends | **Off.** Plain `APIView` does not run `filter_backends`; we do not set `DEFAULT_FILTER_BACKENDS` |

`django-filter` is in dependencies for this path. Do not invent a parallel QuerySerializer-based filter style for list query params.

```mermaid
flowchart LR
    API[APIView] --> SEL[list_posts selector]
    SEL --> BASE[base QS + select_related]
    BASE --> OPT{FilterSet?}
    OPT -->|no| PAG[pagination helper]
    OPT -->|yes| FS["PostFilter(query_params, qs).qs"]
    FS --> PAG
    PAG --> ENV[envelope]
```

### Default — list with no filters

```python
# blogs/selectors/post_selectors.py
def list_posts() -> QuerySet[Post]:
    return (
        Post.objects.filter(status="published")
        .select_related("author", "category")
        .prefetch_related("tags")
        .order_by("-created_at")
    )


# blogs/apis/posts/posts_apis.py
class PostListCreateApiView(ApiAuthMixin, APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 20

    def get(self, request):
        qs = list_posts()
        return get_paginated_response_context(
            pagination_class=self.Pagination,
            serializer_class=PostOutputSerializer,
            queryset=qs,
            request=request,
            view=self,
        )
```

No FilterSet file. No filter query params. Clients only use `limit` / `offset` (or cursor params).

### With filters — `*_search_filters.py` under `apis/`

```text
blogs/apis/posts/
├── posts_apis.py
├── posts_serializers.py
├── posts_search_filters.py   # PostFilter
└── tests/
```

```python
# blogs/apis/posts/posts_search_filters.py
import django_filters

from blogs.models import Post


class PostFilter(django_filters.FilterSet):
    author_id = django_filters.NumberFilter(field_name="author_id")
    # FK / related table — flat query param, ORM lookup with __
    author_email = django_filters.CharFilter(field_name="author__email")
    category_slug = django_filters.CharFilter(field_name="category__slug")
    tag = django_filters.CharFilter(field_name="tags__slug")
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    from_date = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    to_date = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Post
        fields = [
            "author_id",
            "author_email",
            "category_slug",
            "tag",
            "title",
            "from_date",
            "to_date",
        ]
```

```python
# blogs/selectors/post_selectors.py
def list_posts() -> QuerySet[Post]:
    return (
        Post.objects.filter(status="published")
        .select_related("author", "category")
        .prefetch_related("tags")
        .order_by("-created_at")
    )
```

```python
# blogs/apis/posts/posts_apis.py
from blogs.apis.posts.posts_search_filters import PostFilter
from blogs.selectors.post_selectors import list_posts


class PostListCreateApiView(ApiAuthMixin, APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 20

    @extend_schema(
        tags=BLOGS_TAGS,
        summary="List published posts",
        parameters=[PostFilter],  # spectacular / OpenAPI for query params
        responses=PostOutputSerializer,
    )
    def get(self, request):
        qs = list_posts()
        qs = PostFilter(request.query_params, queryset=qs).qs
        return get_paginated_response_context(
            pagination_class=self.Pagination,
            serializer_class=PostOutputSerializer,
            queryset=qs,
            request=request,
            view=self,
        )
```

| Piece | Owns |
|-------|------|
| `PostFilter` | Query-param → ORM filter mapping (FK / dates / …) |
| `list_posts()` | Base QS + `select_related` / `prefetch` (+ auth/ownership scoping) |
| API | Apply FilterSet → paginate → serialize; document FilterSet in OpenAPI |

Example request:

```http
GET /api/v1/blogs/posts/?author_email=a@b.com&tag=django&from_date=2026-01-01&limit=10
```

Only params present in the query string are applied; omitted filters do nothing.

### FK / related filters vs `prefetch`

| Need | What to use |
|------|-------------|
| Filter by related field (`author__email`, `tags__slug`) | `field_name="author__email"` on the FilterSet — **works without prefetch** |
| Avoid N+1 when serializer reads related objects | `select_related` / `prefetch_related` on the **selector** base QS |

Filtering uses SQL joins/lookups. Prefetch is for **reading** related data in the response, not for making filters work. See [Selectors](../layers/selectors.md).

### Ordering / search

Add as FilterSet fields (e.g. `OrderingFilter` from django-filter, or a `CharFilter` mapped carefully). Do **not** set DRF `filter_backends = [OrderingFilter, SearchFilter]` on plain `APIView` and expect them to run automatically.

Document filter params in `@extend_schema(parameters=[PostFilter])` — see [Swagger](swagger.md).

### Naming FilterSets

| Item | Convention | Example |
|------|------------|---------|
| Module | `apis/<route…>/<entity>_search_filters.py` | `posts_search_filters.py`, `pos_search_filters.py` |
| Class | `<Entity>Filter` (singular model name) | `PostFilter`, `PosFilter` |

---

## ❌ Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| `return Response(paginator.get_paginated_response(...).data)` without envelope | Use project `LimitOffsetPagination` / helpers |
| `Model.objects.all()[offset:offset+limit]` in the view | Selector + pagination helper |
| Loading all rows then slicing in Python | DB-level pagination via DRF paginator |
| `PostFilter` under `selectors/` + apply inside `list_*` | `*_search_filters.py` under `apis/` + apply in the view |
| `list_posts(*, request=…)` / `query_params=` on selectors | Selector returns base QS; API owns FilterSet |
| Filter logic copied into 3 views | One FilterSet module next to the list leaf |
| `filter_backends = [...]` on plain `APIView` with no manual invoke | Explicit `FilterSet(..., queryset=qs).qs` in the view |
| Raw `request.query_params.get` + `int(...)` in the view | `FilterSet` fields |
| Parallel `*QuerySerializer` style for the same list filters | One style: django-filter only |
| `max_limit` removed “so mobile can load everything” | Cap limits; offer export endpoints if needed |

---

## ✅ Checklist: list endpoint

1. Selector returns optimized base `QuerySet` (`list_<entities>`)  
2. If the list accepts filters: `<entity>_search_filters.py` next to the list API + apply in `get`  
3. If the list accepts **no** filters: skip the FilterSet entirely  
4. API then paginates  
5. Output serializer only  
6. `@extend_schema(parameters=[…Filter])` when filters exist  
7. API test under that URL leaf: `result.results`, `result.count`, `limit`/`offset` 

---

## 🔗 Related docs

| Doc | Why |
|-----|-----|
| [API envelope](api-envelope.md) | Outer JSON shape |
| [Selectors](../layers/selectors.md) | Where querysets come from |
| [APIs](../layers/apis.md) | View patterns |
| [Swagger](swagger.md) | Documenting query params |
