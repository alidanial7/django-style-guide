from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from {{cookiecutter.project_slug}}.users.models import BaseUser, Profile


class BaseUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = BaseUser
        fields = ("email",)


class BaseUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = BaseUser
        fields = (
            "email",
            "password",
            "is_active",
            "is_admin",
            "is_superuser",
            "groups",
            "user_permissions",
        )


@admin.register(BaseUser)
class BaseUserAdmin(DjangoUserAdmin):
    form = BaseUserChangeForm
    add_form = BaseUserCreationForm
    ordering = ("email",)
    list_display = ("email", "is_active", "is_admin", "is_superuser", "created_at")
    list_filter = ("is_active", "is_admin", "is_superuser")
    search_fields = ("email",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_admin", "is_superuser", "groups", "user_permissions")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_active", "is_admin", "is_superuser"),
            },
        ),
    )

    filter_horizontal = ("groups", "user_permissions")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bio")
    search_fields = ("user__email", "bio")
    raw_id_fields = ("user",)
