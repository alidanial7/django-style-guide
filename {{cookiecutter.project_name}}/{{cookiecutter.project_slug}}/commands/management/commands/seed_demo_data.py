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
        )
{%- else %}
        self.stdout.write(
            f"dry-run — would ensure superuser {LOCAL_ADMIN_EMAIL} / {LOCAL_ADMIN_PASSWORD}"
        )
{%- endif %}
        if DEFAULT_GROUPS:
            self.stdout.write(f"dry-run — would ensure groups: {', '.join(DEFAULT_GROUPS)}")
        else:
            self.stdout.write("dry-run — no default groups configured")
        self.stdout.write("dry-run — no writes")

    def _seed_local_admin(self) -> None:
        """Ensure the local-only superuser exists (dev / demo only)."""
        User = get_user_model()
{%- if cookiecutter.user_login_field == "username" %}
        if User.objects.filter(username=LOCAL_ADMIN_USERNAME).exists():
            self.stdout.write("superuser already exists — skipped")
            return
        User.objects.create_superuser(
            username=LOCAL_ADMIN_USERNAME,
            email=LOCAL_ADMIN_EMAIL,
            password=LOCAL_ADMIN_PASSWORD,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"superuser created: {LOCAL_ADMIN_USERNAME} / {LOCAL_ADMIN_PASSWORD} "
                f"({LOCAL_ADMIN_EMAIL})"
            )
        )
{%- else %}
        if User.objects.filter(email=LOCAL_ADMIN_EMAIL).exists():
            self.stdout.write("superuser already exists — skipped")
            return
        User.objects.create_superuser(
            email=LOCAL_ADMIN_EMAIL,
            password=LOCAL_ADMIN_PASSWORD,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"superuser created: {LOCAL_ADMIN_EMAIL} / {LOCAL_ADMIN_PASSWORD}"
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
