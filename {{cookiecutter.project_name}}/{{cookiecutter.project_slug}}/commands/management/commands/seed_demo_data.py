"""Seed demo / fixture data for local development.

Extend this command when schema changes need matching sample rows.
Do not invent production data here — ask before adding seeds.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Seed local demo data (extend as domain apps grow)."

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
            self.stdout.write("dry-run — no writes")
            return

        # Add domain seeds here (users, catalogs, …). Keep idempotent where possible.
        self.stdout.write(self.style.SUCCESS("seed_demo_data: done (no seeds defined yet)"))
