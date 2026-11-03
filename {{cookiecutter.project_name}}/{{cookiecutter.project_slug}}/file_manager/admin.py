from django.contrib import admin

from {{cookiecutter.project_slug}}.file_manager.models import ManagedFile


@admin.register(ManagedFile)
class ManagedFileAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "is_public",
        "owner",
        "file_size",
        "mime_type",
        "created_at",
    )
    list_filter = ("category", "is_public", "created_at")
    search_fields = ("title", "original_filename", "owner__email")
    raw_id_fields = ("owner",)
    readonly_fields = (
        "id",
        "file_size",
        "mime_type",
        "original_filename",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
