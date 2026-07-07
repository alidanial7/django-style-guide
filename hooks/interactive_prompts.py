"""Interactive terminal UI for the Django Style Guide cookiecutter."""

from __future__ import annotations

import os
import re
import sys
import termios
import tty
from collections.abc import Sequence


class _Colors:
    def __init__(self) -> None:
        interactive = sys.stdin.isatty() and sys.stdout.isatty()
        if interactive:
            self.bold = "\033[1m"
            self.dim = "\033[2m"
            self.cyan = "\033[36m"
            self.green = "\033[32m"
            self.yellow = "\033[33m"
            self.magenta = "\033[35m"
            self.reset = "\033[0m"
            self.hide_cursor = "\033[?25l"
            self.show_cursor = "\033[?25h"
        else:
            self.bold = ""
            self.dim = ""
            self.cyan = ""
            self.green = ""
            self.yellow = ""
            self.magenta = ""
            self.reset = ""
            self.hide_cursor = ""
            self.show_cursor = ""

        self.radio_hint = (
            f"{self.dim}  ↑↓ move  ·  space select  ·  enter confirm{self.reset}"
        )
        self.multiselect_hint = (
            f"{self.dim}  ↑↓ move  ·  space toggle  ·  enter confirm{self.reset}"
        )


COLORS = _Colors()

FEATURE_OPTIONS: tuple[tuple[str, str], ...] = (
    ("use_jwt", "JWT authentication"),
    ("use_sentry", "Sentry monitoring"),
    ("use_vscode", "VS Code configuration"),
    ("use_pgadmin", "pgAdmin (dev)"),
    ("use_redis", "Redis"),
    ("use_rabbitmq", "RabbitMQ"),
    ("use_celery", "Celery"),
    ("use_code_style", "Code style tooling"),
)

DEFAULT_FEATURES: frozenset[str] = frozenset({"use_jwt"})


def slugify(value: str) -> str:
    slug = value.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    return slug.strip("_")


def _cursor_up(lines: int) -> None:
    if lines <= 0:
        return
    sys.stdout.write(f"\033[{lines}A")
    sys.stdout.flush()


def _read_key() -> str:
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
        if key == "\x1b":
            key += sys.stdin.read(2)
        return key
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def prompt_radio(
    title: str,
    help_text: str,
    options: Sequence[tuple[str, str]],
    default_index: int = 0,
) -> str:
    """Radio selector: arrows move focus, space selects, enter confirms."""
    count = len(options)
    focus = min(max(default_index, 0), count - 1)
    selected = focus
    redraw = False
    block_lines = count + 5

    sys.stdout.write(COLORS.hide_cursor)
    sys.stdout.flush()

    try:
        while True:
            if redraw:
                _cursor_up(block_lines)

            print(f"  {COLORS.bold}{title}{COLORS.reset}")
            if help_text:
                print(f"  {COLORS.dim}{help_text}{COLORS.reset}")
            print()

            for index, (_, label) in enumerate(options):
                marker = "•" if index == selected else " "
                pointer = "›" if index == focus else " "
                style = f"{COLORS.bold}{COLORS.green}" if index == focus else ""
                print(
                    f"  {pointer} {style}({marker}) {label}{COLORS.reset}"
                )

            print()
            print(COLORS.radio_hint)

            redraw = True
            key = _read_key()

            if key == "\x1b[A":
                focus = max(0, focus - 1)
            elif key == "\x1b[B":
                focus = min(count - 1, focus + 1)
            elif key == " ":
                selected = focus
            elif key in ("\r", "\n"):
                break
    finally:
        sys.stdout.write(COLORS.show_cursor)
        sys.stdout.flush()

    print()
    return options[selected][0]


def prompt_multiselect(
    title: str,
    help_text: str,
    options: Sequence[tuple[str, str]],
    default_keys: frozenset[str] | set[str] | None = None,
) -> set[str]:
    """Checkbox list: arrows move focus, space toggles, enter confirms."""
    count = len(options)
    focus = 0
    selected = set(default_keys or ())
    redraw = False
    block_lines = count + 5

    sys.stdout.write(COLORS.hide_cursor)
    sys.stdout.flush()

    try:
        while True:
            if redraw:
                _cursor_up(block_lines)

            print(f"  {COLORS.bold}{title}{COLORS.reset}")
            if help_text:
                print(f"  {COLORS.dim}{help_text}{COLORS.reset}")
            print()

            for index, (key, label) in enumerate(options):
                marker = "•" if key in selected else " "
                pointer = "›" if index == focus else " "
                style = f"{COLORS.bold}{COLORS.green}" if index == focus else ""
                print(f"  {pointer} {style}({marker}) {label}{COLORS.reset}")

            print()
            print(COLORS.multiselect_hint)

            redraw = True
            key = _read_key()

            if key == "\x1b[A":
                focus = max(0, focus - 1)
            elif key == "\x1b[B":
                focus = min(count - 1, focus + 1)
            elif key == " ":
                option_key = options[focus][0]
                if option_key in selected:
                    selected.remove(option_key)
                else:
                    selected.add(option_key)
            elif key in ("\r", "\n"):
                break
    finally:
        sys.stdout.write(COLORS.show_cursor)
        sys.stdout.flush()

    print()
    return selected


def yn(selected_keys: set[str], key: str) -> str:
    return "y" if key in selected_keys else "n"


def format_feature_summary(selected_keys: set[str]) -> str:
    enabled = [label for key, label in FEATURE_OPTIONS if key in selected_keys]
    if not enabled:
        return "none"
    return ", ".join(enabled)


def prompt_radio_yn(title: str, help_text: str, default: str = "y") -> str:
    default_index = 0 if default == "y" else 1
    return prompt_radio(
        title,
        help_text,
        (("y", "Yes"), ("n", "No")),
        default_index=default_index,
    )


def prompt_text(label: str, default: str = "") -> str:
    print(f"  {COLORS.bold}{label}{COLORS.reset}")
    if default:
        print(
            f"  {COLORS.dim}›{COLORS.reset} "
            f"[{COLORS.green}{default}{COLORS.reset}]: ",
            end="",
        )
    else:
        print(f"  {COLORS.dim}›{COLORS.reset} ", end="")
    sys.stdout.flush()

    value = input().strip()
    return value or default


def print_banner() -> None:
    c = COLORS
    print()
    print(
        f"{c.cyan}{c.bold}  ╔══════════════════════════════════════════════════════════════╗{c.reset}"
    )
    print(
        f"{c.cyan}{c.bold}  ║         Django Style Guide — Project Generator               ║{c.reset}"
    )
    print(
        f"{c.cyan}{c.bold}  ║                                                              ║{c.reset}"
    )
    print(
        f"{c.cyan}{c.bold}  ║   HackSoft structure  ·  Docker Compose  ·  DRF  ·  Celery   ║{c.reset}"
    )
    print(
        f"{c.cyan}{c.bold}  ╚══════════════════════════════════════════════════════════════╝{c.reset}"
    )
    print()


def print_section(title: str) -> None:
    c = COLORS
    print()
    print(f"{c.magenta}{c.bold}  ── {title} ──{c.reset}")
    print()


def collect_answers() -> dict[str, str] | None:
    """Run the interactive wizard. Returns None when the user cancels."""
    print_banner()

    print_section("Project")
    project_name = prompt_text("Project name", "MyProject")
    default_slug = slugify(project_name)
    project_slug = prompt_text("Project slug (Python package)", default_slug) or default_slug

    print_section("Author")
    first_name = prompt_text("First name", "author")
    last_name = prompt_text("Last name", "author lastname")

    print_section("License")
    license_choice = prompt_radio(
        "License",
        "Choose a license for the generated project.",
        (("MIT", "MIT"), ("BEER", "BEER"), ("None", "None (no LICENSE file)")),
        default_index=0,
    )

    print_section("Database defaults")
    postgres_user = prompt_text("PostgreSQL user", "user")
    postgres_password = prompt_text("PostgreSQL password", "password")

    print_section("Features")
    selected_features = prompt_multiselect(
        "Features",
        "Select the optional components to include in your project.",
        FEATURE_OPTIONS,
        default_keys=DEFAULT_FEATURES,
    )

    use_jwt = yn(selected_features, "use_jwt")
    use_sentry = yn(selected_features, "use_sentry")
    use_vscode = yn(selected_features, "use_vscode")
    use_pgadmin = yn(selected_features, "use_pgadmin")
    use_redis = yn(selected_features, "use_redis")
    use_rabbitmq = yn(selected_features, "use_rabbitmq")
    use_celery = yn(selected_features, "use_celery")
    use_code_style = yn(selected_features, "use_code_style")

    if use_celery == "y" and use_rabbitmq != "y":
        print()
        print(
            f"  {COLORS.yellow}↳ Celery requires RabbitMQ — RabbitMQ will be enabled.{COLORS.reset}"
        )
        use_rabbitmq = "y"
        selected_features.add("use_rabbitmq")

    print_section("Summary")
    c = COLORS
    print(
        f"  {c.bold}Project{c.reset}     {project_name} {c.dim}({project_slug}){c.reset}"
    )
    print(f"  {c.bold}License{c.reset}     {license_choice}")
    print(
        f"  {c.bold}Features{c.reset}    {format_feature_summary(selected_features)}"
    )
    print()

    confirm = prompt_radio_yn(
        "Generate project?",
        "Create the project with these settings.",
        "y",
    )
    if confirm == "n":
        print(f"  {COLORS.dim}Cancelled.{COLORS.reset}")
        return None

    return {
        "project_name": project_name,
        "project_slug": project_slug,
        "first_name": first_name,
        "last_name": last_name,
        "license": license_choice,
        "postgres_user": postgres_user,
        "postgres_password": postgres_password,
        "use_jwt": use_jwt,
        "use_sentry": use_sentry,
        "use_vscode": use_vscode,
        "use_pgadmin": use_pgadmin,
        "use_redis": use_redis,
        "use_rabbitmq": use_rabbitmq,
        "use_celery": use_celery,
        "use_code_style": use_code_style,
    }


def generate_project(repo_dir: str, output_dir: str, answers: dict[str, str]) -> None:
    """Generate the project with cookiecutter, skipping this hook's UI."""
    os.environ["DSG_COOKIECUTTER_SKIP_PROMPT_UI"] = "1"

    from cookiecutter.main import cookiecutter

    c = COLORS
    print()
    print(f"{c.cyan}{c.bold}  Generating project...{c.reset}")
    print()

    cookiecutter(
        repo_dir,
        no_input=True,
        extra_context=answers,
        output_dir=output_dir,
        accept_hooks=True,
        overwrite_if_exists=False,
    )

    project_name = answers["project_name"]
    print()
    print(
        f"{c.green}{c.bold}  ✓ Done!{c.reset}  "
        f"{c.dim}cd {project_name} && see README.md{c.reset}"
    )
    print()


def run_cli(repo_dir: str) -> int:
    """Entry point for init.sh and other local wrappers."""
    answers = collect_answers()
    if answers is None:
        return 0

    output_dir = os.environ.get("PWD") or "."
    generate_project(repo_dir, output_dir, answers)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: interactive_prompts.py <template-directory>", file=sys.stderr)
        sys.exit(2)
    sys.exit(run_cli(sys.argv[1]))
