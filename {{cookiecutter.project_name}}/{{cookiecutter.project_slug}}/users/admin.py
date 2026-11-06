from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from {{cookiecutter.project_slug}}.users.models import BaseUser, Profile
{%- if cookiecutter.use_google_login == "y" or cookiecutter.use_microsoft_login == "y" or cookiecutter.use_apple_login == "y" %}
from {{cookiecutter.project_slug}}.users.models import SocialAccount
{%- endif %}


class BaseUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):  # type: ignore[name-defined]
        model = BaseUser
{%- if cookiecutter.user_login_field == "username" and cookiecutter.use_otp_login == "y" %}
        fields = ("username", "email", "phone")
{%- elif cookiecutter.user_login_field == "username" %}
        fields = ("username", "email")
{%- elif cookiecutter.use_otp_login == "y" %}
        fields = ("email", "phone")
{%- else %}
        fields = ("email",)
{%- endif %}


class BaseUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):  # type: ignore[name-defined]
        model = BaseUser
{%- if cookiecutter.user_login_field == "username" and cookiecutter.use_otp_login == "y" %}
        fields = (
            "username",
            "email",
            "phone",
            "password",
            "is_active",
            "is_admin",
            "is_superuser",
            "groups",
            "user_permissions",
        )
{%- elif cookiecutter.user_login_field == "username" %}
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
{%- elif cookiecutter.use_otp_login == "y" %}
        fields = (
            "email",
            "phone",
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
{%- if cookiecutter.user_login_field == "username" and cookiecutter.use_otp_login == "y" %}
    ordering = ("username",)
    list_display = ("username", "email", "phone", "is_active", "is_admin", "is_superuser", "created_at")
    search_fields = ("username", "email", "phone")
{%- elif cookiecutter.user_login_field == "username" %}
    ordering = ("username",)
    list_display = ("username", "email", "is_active", "is_admin", "is_superuser", "created_at")
    search_fields = ("username", "email")
{%- elif cookiecutter.use_otp_login == "y" %}
    ordering = ("email",)
    list_display = ("email", "phone", "is_active", "is_admin", "is_superuser", "created_at")
    search_fields = ("email", "phone")
{%- else %}
    ordering = ("email",)
    list_display = ("email", "is_active", "is_admin", "is_superuser", "created_at")
    search_fields = ("email",)
{%- endif %}
    list_filter = ("is_active", "is_admin", "is_superuser")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
{%- if cookiecutter.user_login_field == "username" and cookiecutter.use_otp_login == "y" %}
        (None, {"fields": ("username", "email", "phone", "password")}),
{%- elif cookiecutter.user_login_field == "username" %}
        (None, {"fields": ("username", "email", "password")}),
{%- elif cookiecutter.use_otp_login == "y" %}
        (None, {"fields": ("email", "phone", "password")}),
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


{%- if cookiecutter.use_google_login == "y" or cookiecutter.use_microsoft_login == "y" or cookiecutter.use_apple_login == "y" %}
@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ("provider", "subject", "user", "created_at")
    list_filter = ("provider",)
    search_fields = ("subject", "user__email")
    raw_id_fields = ("user",)
{%- endif %}