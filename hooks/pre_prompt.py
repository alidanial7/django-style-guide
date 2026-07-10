#!/usr/bin/env python3
"""Optional notice before cookiecutter's built-in prompts.

Interactive checklist UI lives in ``init.sh`` / ``hooks/interactive_prompts.py``.
Plain ``cookiecutter`` uses the standard prompts from ``cookiecutter.json``.
"""

from __future__ import annotations

import os
import sys

SKIP_ENV = "DSG_COOKIECUTTER_SKIP_PROMPT_UI"


def main() -> None:
    if os.environ.get(SKIP_ENV):
        return

    if not sys.stdin.isatty():
        return

    # Do not hijack the parent cookiecutter process. Point TTY users at init.sh
    # for the richer UI; otherwise continue with cookiecutter's own prompts.
    sys.stderr.write(
        "\n"
        "  Tip: for the interactive checklist UI, run ./init.sh from a clone,\n"
        "  or: python hooks/interactive_prompts.py <template-dir>\n"
        "  Continuing with cookiecutter's standard prompts…\n"
        "\n"
    )


if __name__ == "__main__":
    main()
