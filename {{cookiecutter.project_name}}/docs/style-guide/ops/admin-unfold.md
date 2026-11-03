# Unfold admin

Optional [django-unfold](https://github.com/unfoldadmin/django-unfold) skin for Django admin.
Enabled at cookiecutter generation; related files are removed when the option is off.

## Layout

| Piece | Location |
|-------|----------|
| Settings | `config/settings/unfold.py` (`UNFOLD` dict) |
| Shared admin app | `{{cookiecutter.project_slug}}/administration/` |
| Per-domain registration | `<app>/admin.py` |
| URL mount | `config/urls.py` → default `path("admin/", …)` |

`administration/` holds shared widgets, mixins, templates (`templates/administration/`), and static assets. Domain models still register in their own app.

## Hard rules

| Do | Don’t |
|----|-------|
| Subclass `unfold.admin.ModelAdmin` | Use stock `admin.ModelAdmin` when Unfold is on |
| Put shared admin UI in `administration/` | Dump cross-app widgets into a random domain app |
| `reverse` / `reverse_lazy("admin:…")` for links | Hardcode `/admin/...` strings |
| Update `<app>/admin.py` on every model create/change | Leave admin stale after field/model edits |
| Read mount path from URLconf / settings | Assume a non-default admin prefix in code or docs |
| Keep `UNFOLD["SIDEBAR"]["navigation"]` in sync with real changelists | Orphan sidebar items pointing at missing models |

## ModelAdmin baseline

```python
from unfold.admin import ModelAdmin
from django.contrib import admin

from .models import Example


@admin.register(Example)
class ExampleAdmin(ModelAdmin):
    list_display = ("id", "name", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
```

On model change: refresh `list_display`, `list_filter`, `search_fields`, `readonly_fields`, and fieldsets.

## Settings stub

`UNFOLD` sets `SITE_TITLE` / `SITE_HEADER` from the project name and a sidebar navigation stub (Dashboard → `admin:index`). Extend `navigation` with domain sections; prefer named admin routes for `link`.

## URL mount

Default remains `/admin/`. If the mount path changes later, update only the URLconf and any reverse names — never sprinkle path literals through templates or sidebar config.

## Checklist

1. New/changed model → sync that app’s `admin.py` with Unfold `ModelAdmin`.
2. Shared widget/template → `administration/` (+ static/templates dirs).
3. Sidebar / deep links → `reverse_lazy`, not hardcoded `/admin/…`.
4. Confirm admin still loads at the configured mount path after URL changes.

Related: [Settings](settings.md) · [Models](../domain/models.md)
