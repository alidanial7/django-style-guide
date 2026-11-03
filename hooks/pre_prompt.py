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
import subprocess
import sys
from pathlib import Path

SKIP_ENV = "DSG_COOKIECUTTER_SKIP_PROMPT_UI"


def _parent_has_no_input() -> bool:
    try:
        proc_cmd = Path(f"/proc/{os.getppid()}/cmdline")
        if proc_cmd.exists():
            return "--no-input" in proc_cmd.read_text()
        cmd = subprocess.check_output(
            ["ps", "-o", "args=", "-p", str(os.getppid())],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return "--no-input" in cmd
    except Exception:
        return False


def _stop_outer_cookiecutter_run() -> None:
    """End the parent cookiecutter process after we already generated the project.

    The outer ``cookiecutter`` invocation cannot skip its own prompts after
    ``pre_prompt`` finishes, so we terminate it once generation is done.
    The shell may exit with code 143 (SIGTERM) — that is expected and means success.
    """
    sys.stdout.flush()
    sys.stderr.flush()
    try:
        os.kill(os.getppid(), getattr(signal, "SIGTERM", 15))
    except (OSError, AttributeError):
        pass
    os._exit(0)


def main() -> None:
    if os.environ.get(SKIP_ENV) or _parent_has_no_input():
        return

    if not sys.stdin.isatty():
        return

    hooks_dir = Path(__file__).resolve().parent
    if str(hooks_dir) not in sys.path:
        sys.path.insert(0, str(hooks_dir))

    repo_dir = str(hooks_dir.parent)
    output_dir = os.environ.get("PWD")
    if not output_dir or not Path(output_dir).is_dir():
        output_dir = "."

    from interactive_prompts import collect_answers, generate_project

    answers = collect_answers()
    if answers is None:
        # User cancelled — stop the outer cookiecutter as well.
        _stop_outer_cookiecutter_run()

    generate_project(repo_dir, output_dir, answers)
    _stop_outer_cookiecutter_run()


if __name__ == "__main__":
    main()
