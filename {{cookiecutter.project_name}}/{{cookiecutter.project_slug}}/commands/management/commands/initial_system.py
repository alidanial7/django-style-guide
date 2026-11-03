"""One-shot system bootstrap hooks (groups, feature flags, required rows).

Prefer idempotent steps. For day-to-day local boot use ``devserver``.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Initialize required system rows (extend as needed)."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print planned work without writing.",
        )

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        dry_run: bool = options["dry_run"]
        self.stdout.write(self.style.NOTICE("initial_system: starting"))
        if dry_run:
            self.stdout.write("dry-run — no writes")
            return

        # Examples: ensure default groups, feature flags, catalog roots.
        self.stdout.write(self.style.SUCCESS("initial_system: done (no steps defined yet)"))
