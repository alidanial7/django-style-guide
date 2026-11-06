from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from {{cookiecutter.project_slug}}.users.models import BaseUser, Profile


class BaseUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = BaseUser
{%- if cookiecutter.user_login_field == "username" %}
        fields = ("username", "email")
{%- else %}
        fields = ("email",)
{%- endif %}


class BaseUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = BaseUser
{%- if cookiecutter.user_login_field == "username" %}
        fields = (
            "username",
            "email",
            "password",
            "is_active",
            "is_admin",
            "is_superuser",
            "groups",
            "user_permissions",
        )
{%- else %}
        fields = (
            "email",
            "password",
            "is_active",
            "is_admin",
            "is_superuser",
            "groups",
            "user_permissions",
        )
{%- endif %}


@admin.register(BaseUser)
class BaseUserAdmin(DjangoUserAdmin):
    form = BaseUserChangeForm
    add_form = BaseUserCreationForm
{%- if cookiecutter.user_login_field == "username" %}
    ordering = ("username",)
    list_display = ("username", "email", "is_active", "is_admin", "is_superuser", "created_at")
    search_fields = ("username", "email")
{%- else %}
    ordering = ("email",)
    list_display = ("email", "is_active", "is_admin", "is_superuser", "created_at")
    search_fields = ("email",)
{%- endif %}
    list_filter = ("is_active", "is_admin", "is_superuser")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
{%- if cookiecutter.user_login_field == "username" %}
        (None, {"fields": ("username", "email", "password")}),
{%- else %}
        (None, {"fields": ("email", "password")}),
{%- endif %}
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
{%- if cookiecutter.user_login_field == "username" %}
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "is_active",
                    "is_admin",
                    "is_superuser",
                ),
{%- else %}
                "fields": ("email", "password1", "password2", "is_active", "is_admin", "is_superuser"),
{%- endif %}
            },
        ),
    )

    filter_horizontal = ("groups", "user_permissions")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bio")
{%- if cookiecutter.user_login_field == "username" %}
    search_fields = ("user__username", "user__email", "bio")
{%- else %}
    search_fields = ("user__email", "bio")
{%- endif %}
    raw_id_fields = ("user",)
