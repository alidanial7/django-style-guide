#!/usr/bin/env python3
"""Run the interactive generator before cookiecutter's built-in prompts."""

from __future__ import annotations

import os
import sys
from pathlib import Path

SKIP_ENV = "DSG_COOKIECUTTER_SKIP_PROMPT_UI"


def main() -> None:
    if os.environ.get(SKIP_ENV):
        return

    if not sys.stdin.isatty():
        return

    repo_dir = str(Path.cwd())
    output_dir = os.environ.get("PWD") or "."

    # Import from the hooks package directory.
    hooks_dir = Path(__file__).resolve().parent
    if str(hooks_dir) not in sys.path:
        sys.path.insert(0, str(hooks_dir))

    from interactive_prompts import collect_answers, generate_project

    answers = collect_answers()
    if answers is None:
        sys.exit(0)

    try:
        generate_project(repo_dir, output_dir, answers)
    except Exception:
        raise

    # Generation finished in the nested cookiecutter run. Stop the parent
    # invocation so it does not prompt again or try to regenerate.
    print(
        "  Note: cookiecutter may report a hook error below — "
        "that is expected after generation completes."
    )
    print()
    sys.exit(1)


if __name__ == "__main__":
    main()
