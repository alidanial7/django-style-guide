"""Seed local / demo data.

Run::

    python manage.py seed_demo_data
    python manage.py seed_demo_data --dry-run

Always idempotent. Extend by adding private ``_seed_*`` methods and calling
them from ``handle``. Schema change that needs sample rows → update this
command in the same change (ask before inventing production-like data).
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction

{% if cookiecutter.user_login_field == "username" -%}
LOCAL_ADMIN_USERNAME = "admin"
LOCAL_ADMIN_EMAIL = "admin@example.com"
LOCAL_ADMIN_PASSWORD = "admin"
{% else -%}
LOCAL_ADMIN_EMAIL = "admin@example.com"
LOCAL_ADMIN_PASSWORD = "admin"
{% endif %}
{%- if cookiecutter.use_otp_login == "y" %}
# Same sample number as phone validator docs (E.164 digits, no '+').
LOCAL_ADMIN_PHONE = "989123456789"
{%- endif %}

# Named groups to ensure on every seed (extend as portals / roles grow).
{% if cookiecutter.use_portal_permissions == "y" -%}
DEFAULT_GROUPS: tuple[str, ...] = (
    "admin",
    "customer",
)
{% else -%}
DEFAULT_GROUPS: tuple[str, ...] = ()  # e.g. ("editors", "support")
{% endif %}


class Command(BaseCommand):
    help = "Seed local demo data (default admin, groups, …). Idempotent."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print planned work without writing.",
        )

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        dry_run: bool = options["dry_run"]
        self.stdout.write(self.style.NOTICE("seed_demo_data: starting"))

        if dry_run:
            self._plan_dry_run()
            return

        self._seed_local_admin()
{%- if cookiecutter.use_scoped_apis == "y" %}
        self._seed_scope_users()
{%- endif %}
        self._seed_groups()
        # Add more steps here, e.g.:
        # self._seed_catalog()
        # self._seed_demo_users()

        self.stdout.write(self.style.SUCCESS("seed_demo_data: done"))

    def _plan_dry_run(self) -> None:
{%- if cookiecutter.user_login_field == "username" %}
        self.stdout.write(
            "dry-run — would ensure superuser "
            f"{LOCAL_ADMIN_USERNAME} / {LOCAL_ADMIN_EMAIL} / {LOCAL_ADMIN_PASSWORD}"
{%- if cookiecutter.use_otp_login == "y" %}
            f" / phone {LOCAL_ADMIN_PHONE}"
{%- endif %}
        )
{%- else %}
        self.stdout.write(
            f"dry-run — would ensure superuser {LOCAL_ADMIN_EMAIL} / {LOCAL_ADMIN_PASSWORD}"
{%- if cookiecutter.use_otp_login == "y" %}
            f" / phone {LOCAL_ADMIN_PHONE}"
{%- endif %}
        )
{%- endif %}
        if DEFAULT_GROUPS:
            self.stdout.write(f"dry-run — would ensure groups: {', '.join(DEFAULT_GROUPS)}")
        else:
            self.stdout.write("dry-run — no default groups configured")
{%- if cookiecutter.use_scoped_apis == "y" %}
        self.stdout.write(
            "dry-run — would ensure one user per API scope "
            "(username/password = scope name"
{%- if cookiecutter.use_otp_login == "y" %}
            ", phones 989120000001, 989120000002, …"
{%- endif %}
            ")"
        )
{%- endif %}
        self.stdout.write("dry-run — no writes")

    def _seed_local_admin(self) -> None:
        """Ensure the local-only superuser exists (dev / demo only)."""
        User = get_user_model()
{%- if cookiecutter.user_login_field == "username" %}
        existing = User.objects.filter(username=LOCAL_ADMIN_USERNAME).first()
        if existing is not None:
{%- if cookiecutter.use_otp_login == "y" %}
            if existing.phone != LOCAL_ADMIN_PHONE:
                existing.phone = LOCAL_ADMIN_PHONE
                existing.save(update_fields=["phone"])
                self.stdout.write(
                    self.style.SUCCESS(
                        f"superuser phone set: {LOCAL_ADMIN_PHONE}"
                    )
                )
            else:
                self.stdout.write("superuser already exists — skipped")
{%- else %}
            self.stdout.write("superuser already exists — skipped")
{%- endif %}
            return
        User.objects.create_superuser(
            username=LOCAL_ADMIN_USERNAME,
            email=LOCAL_ADMIN_EMAIL,
            password=LOCAL_ADMIN_PASSWORD,
{%- if cookiecutter.use_otp_login == "y" %}
            phone=LOCAL_ADMIN_PHONE,
{%- endif %}
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"superuser created: {LOCAL_ADMIN_USERNAME} / {LOCAL_ADMIN_PASSWORD} "
                f"({LOCAL_ADMIN_EMAIL})"
{%- if cookiecutter.use_otp_login == "y" %}
                f" / {LOCAL_ADMIN_PHONE}"
{%- endif %}
            )
        )
{%- else %}
        existing = User.objects.filter(email=LOCAL_ADMIN_EMAIL).first()
        if existing is not None:
{%- if cookiecutter.use_otp_login == "y" %}
            if existing.phone != LOCAL_ADMIN_PHONE:
                existing.phone = LOCAL_ADMIN_PHONE
                existing.save(update_fields=["phone"])
                self.stdout.write(
                    self.style.SUCCESS(
                        f"superuser phone set: {LOCAL_ADMIN_PHONE}"
                    )
                )
            else:
                self.stdout.write("superuser already exists — skipped")
{%- else %}
            self.stdout.write("superuser already exists — skipped")
{%- endif %}
            return
        User.objects.create_superuser(
            email=LOCAL_ADMIN_EMAIL,
            password=LOCAL_ADMIN_PASSWORD,
{%- if cookiecutter.use_otp_login == "y" %}
            phone=LOCAL_ADMIN_PHONE,
{%- endif %}
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"superuser created: {LOCAL_ADMIN_EMAIL} / {LOCAL_ADMIN_PASSWORD}"
{%- if cookiecutter.use_otp_login == "y" %}
                f" / {LOCAL_ADMIN_PHONE}"
{%- endif %}
            )
        )
{%- endif %}

    def _seed_groups(self) -> None:
        """Ensure named auth groups exist. Add role wiring in services/permissions as needed."""
        if not DEFAULT_GROUPS:
            self.stdout.write("groups: none configured — skipped")
            return

        created_names: list[str] = []
        for name in DEFAULT_GROUPS:
            _group, created = Group.objects.get_or_create(name=name)
            if created:
                created_names.append(name)

        if created_names:
            self.stdout.write(self.style.SUCCESS(f"groups created: {', '.join(created_names)}"))
        else:
            self.stdout.write("groups already exist — skipped")

{%- if cookiecutter.use_scoped_apis == "y" %}
    def _seed_scope_users(self) -> None:
        """One local user per API scope: login + password = scope name."""
        from django.conf import settings

        from {{cookiecutter.project_slug}}.users.scope_registry import get_scope_user_model
        from {{cookiecutter.project_slug}}.users.services.scope_membership import (
            ensure_scope_membership,
        )

        User = get_user_model()
        scopes = list(getattr(settings, "API_SCOPES", ()) or ())
        for index, scope in enumerate(scopes, start=1):
            model = get_scope_user_model(scope=scope)
{%- if cookiecutter.use_otp_login == "y" %}
            phone = f"98912{index:07d}"
{%- endif %}
{%- if cookiecutter.user_login_field == "username" %}
            email = (
                LOCAL_ADMIN_EMAIL if scope == "admin" else f"{scope}@example.com"
            )
            existing = User.objects.filter(username=scope).first()
{%- else %}
            email = (
                LOCAL_ADMIN_EMAIL if scope == "admin" else f"{scope}@example.com"
            )
            existing = User.objects.filter(email=email).first()
{%- endif %}
            is_super = scope == "admin"
            if existing is None:
{%- if cookiecutter.user_login_field == "username" %}
                creator = (
                    model.objects.create_superuser
                    if is_super
                    else model.objects.create_user
                )
                creator(
                    scope,
                    email,
                    password=scope,
{%- if cookiecutter.use_otp_login == "y" %}
                    phone=phone,
{%- endif %}
                )
{%- else %}
                if is_super:
                    model.objects.create_superuser(
                        email,
                        password=scope,
{%- if cookiecutter.use_otp_login == "y" %}
                        phone=phone,
{%- endif %}
                    )
                else:
                    model.objects.create_user(
                        email,
                        password=scope,
{%- if cookiecutter.use_otp_login == "y" %}
                        phone=phone,
{%- endif %}
                    )
{%- endif %}
                self.stdout.write(
                    self.style.SUCCESS(
                        f"scope user created: {scope} / {scope} ({email})"
{%- if cookiecutter.use_otp_login == "y" %}
                        f" / {phone}"
{%- endif %}
                    )
                )
                continue

            changed: list[str] = []
{%- if cookiecutter.use_otp_login == "y" %}
            if existing.phone != phone:
                existing.phone = phone
                changed.append("phone")
{%- endif %}
            if is_super and not existing.is_superuser:
                existing.is_superuser = True
                existing.is_admin = True
                changed.extend(["is_superuser", "is_admin"])
            if changed:
                existing.save(update_fields=changed)
            if not model.objects.filter(pk=existing.pk).exists():
                ensure_scope_membership(user=existing, scope=scope)
                changed.append("membership")
            if changed:
                self.stdout.write(
                    self.style.SUCCESS(f"scope user updated ({scope}): {', '.join(changed)}")
                )
            else:
                self.stdout.write(f"scope user {scope} already exists — skipped")
{%- endif %}
