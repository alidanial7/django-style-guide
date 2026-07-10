#!/usr/bin/env python3
"""Run the interactive checklist UI before cookiecutter's built-in prompts.

When stdin is a TTY, this hook generates the project itself and then stops the
outer cookiecutter process so the user is not asked 28 times again.

Non-interactive / ``--no-input`` runs skip this hook's UI (via
``DSG_COOKIECUTTER_SKIP_PROMPT_UI`` or a non-TTY stdin) and use cookiecutter's
standard prompts / defaults.
"""

from __future__ import annotations

import os
import signal
import sys
from pathlib import Path

SKIP_ENV = "DSG_COOKIECUTTER_SKIP_PROMPT_UI"


def _stop_outer_cookiecutter_run() -> None:
    """End the parent cookiecutter process after we already generated the project.

    The outer ``cookiecutter`` invocation cannot skip its own prompts after
    ``pre_prompt`` finishes, so we terminate it once generation is done.
    The shell may exit with code 143 (SIGTERM) — that is expected and means success.
    """
    sys.stdout.flush()
    sys.stderr.flush()
    try:
        os.kill(os.getppid(), signal.SIGTERM)
    except OSError:
        pass
    os._exit(0)


def main() -> None:
    if os.environ.get(SKIP_ENV):
        return

    if not sys.stdin.isatty():
        return

    repo_dir = str(Path.cwd())
    output_dir = os.environ.get("PWD") or "."

    hooks_dir = Path(__file__).resolve().parent
    if str(hooks_dir) not in sys.path:
        sys.path.insert(0, str(hooks_dir))

    from interactive_prompts import collect_answers, generate_project

    answers = collect_answers()
    if answers is None:
        # User cancelled — stop the outer cookiecutter as well.
        _stop_outer_cookiecutter_run()

    generate_project(repo_dir, output_dir, answers)
    _stop_outer_cookiecutter_run()


if __name__ == "__main__":
    main()
