# 🏢 Enterprise extensions (out of scope)

> Patterns common in large systems that this blueprint **does not ship**.
>
> Use this page so teams and agents do not invent conflicting layouts — extend deliberately.

---

## Explicitly not included

| Concern | Guidance if you add it |
|---------|------------------------|
| Soft delete (`deleted_at`) | Prefer explicit queryset managers (`alive()`); never rely on signals alone; index `deleted_at` |
| `created_by` / audit columns | Add on `BaseModel` subclasses or a separate audit table; set in **services**, not serializers |
| Full RBAC / scopes | Permission classes + optional policy module under the domain app; keep HTTP checks out of selectors |
| Multi-tenancy | Tenant id on rows + selector filters mandatory; never trust client tenant id without auth binding |
| Idempotency-Key for POST | Middleware or service-layer store (Redis) keyed by actor + key; return same result on replay |
| Transactional outbox / domain events | Outbox table written in the same DB transaction as the aggregate; Celery/relay publishes later |
| Read replicas | Django DB routers; selectors may use `using("replica")` — document lag tolerance |
| Feature flags | External system or settings-backed flags read in services — not scattered `if` in views |

---

## What this blueprint already covers

| Need | Where |
|------|-------|
| Layered domain apps | [Architecture](../overview/architecture.md), [Domain apps](../overview/domain-apps.md) |
| Safe writes + integrity | [Services](../domain/services.md), [Validation](../domain/validation.md) |
| Deny-by-default API security | [Security](../http/security.md), [Permissions](../http/permissions.md) |
| Stable list pagination | [Pagination](../http/pagination.md) (`LimitOffset` + `Cursor`) |
| Zero-downtime schema habits | [Migrations](../ops/migrations.md) |
| Async jobs (optional) | [Celery](../ops/celery.md) when generated with Celery |
| Realtime (optional) | [WebSockets](../ops/websockets.md) when generated with Channels |

---

## Rule for agents

If a feature needs a row above, **ask / propose an explicit design** rather than silently adding a parallel architecture (e.g. fat models, global utils, or a second exception handler).
