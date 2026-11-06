"""Extract / refresh gettext catalogs under project ``locale/``.

Examples::

    python manage.py update_translations
    python manage.py update_translations --locale fa
    python manage.py update_translations --compile
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Update project gettext .po files (and optionally compile .mo)."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--locale",
            action="append",
            dest="locales",
            default=[],
            help="Locale code to create/update (repeatable), e.g. --locale fa. "
            "Default: all languages in settings.LANGUAGES.",
        )
        parser.add_argument(
            "--compile",
            action="store_true",
            help="Run compilemessages after updating .po files.",
        )
        parser.add_argument(
            "--no-clean",
            action="store_true",
            help="Skip msgattrib / msgcat cleanup of .po files.",
        )

    def handle(self, *args, **options) -> None:
        if not getattr(settings, "USE_I18N", False):
            raise CommandError(
                "USE_I18N is disabled; enable use_i18n when generating the project."
            )

        locale_root = self._locale_root()
        locale_root.mkdir(parents=True, exist_ok=True)

        locales: list[str] = list(options["locales"])
        if not locales:
            locales = [code for code, _name in getattr(settings, "LANGUAGES", ())]
        if not locales:
            locales = [str(settings.LANGUAGE_CODE).replace("_", "-").split("-")[0]]

        ignore = [
            "venv",
            ".venv",
            "*/site-packages/*",
            "node_modules",
            "staticfiles",
            "media",
        ]

        self.stdout.write(self.style.NOTICE("update_translations: starting"))
        for locale in locales:
            self.stdout.write(f"makemessages -l {locale}")
            call_command(
                "makemessages",
                locale=[locale],
                ignore=ignore,
                no_location=True,
                no_wrap=True,
                extension=["html", "txt", "py"],
            )

        if not options["no_clean"]:
            self._clean_po_files(locale_root=locale_root)

        if options["compile"]:
            self.stdout.write("compilemessages")
            call_command("compilemessages", ignore=["venv", ".venv", "node_modules"])

        self.stdout.write(self.style.SUCCESS("update_translations: done"))

    def _locale_root(self) -> Path:
        paths = getattr(settings, "LOCALE_PATHS", ()) or ()
        if not paths:
            raise CommandError("LOCALE_PATHS is empty; check config/settings/i18n.py.")
        return Path(paths[0])

    def _clean_po_files(self, *, locale_root: Path) -> None:
        msgattrib = shutil.which("msgattrib")
        msgcat = shutil.which("msgcat")
        if not msgattrib or not msgcat:
            self.stdout.write(
                self.style.WARNING(
                    "gettext tools (msgattrib/msgcat) not found — skipping .po cleanup. "
                    "Install gettext (e.g. brew install gettext)."
                )
            )
            return

        project_root = locale_root.parent
        for po_file in locale_root.glob("*/LC_MESSAGES/*.po"):
            self.stdout.write(f"cleaning {po_file.relative_to(project_root)}")
            text = po_file.read_text(encoding="utf-8")
            lines = [
                line
                for line in text.splitlines(keepends=True)
                if not line.startswith('"POT-Creation-Date:')
            ]
            po_file.write_text("".join(lines), encoding="utf-8")

            cleaned = tempfile.NamedTemporaryFile(delete=False)
            cleaned_path = Path(cleaned.name)
            cleaned.close()
            sorted_tmp = tempfile.NamedTemporaryFile(delete=False)
            sorted_path = Path(sorted_tmp.name)
            sorted_tmp.close()
            try:
                subprocess.run(
                    [msgattrib, "--no-obsolete", "-o", str(cleaned_path), str(po_file)],
                    check=True,
                )
                shutil.move(str(cleaned_path), po_file)
                subprocess.run(
                    [msgcat, "--sort-output", "-o", str(sorted_path), str(po_file)],
                    check=True,
                )
                shutil.move(str(sorted_path), po_file)
            finally:
                cleaned_path.unlink(missing_ok=True)
                sorted_path.unlink(missing_ok=True)
