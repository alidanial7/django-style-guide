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
    ("use_jwt", "JWT authentication (off = session auth)"),
    ("use_sentry", "Sentry monitoring"),
    ("use_vscode", "VS Code configuration"),
    ("use_pgadmin", "pgAdmin (dev)"),
    ("use_redis", "Redis"),
    ("use_rabbitmq", "RabbitMQ"),
    ("use_celery", "Celery"),
    ("use_asgi", "ASGI (Uvicorn)"),
    ("use_websockets", "WebSockets (Django Channels)"),
    ("use_code_style", "Code style tooling"),
    ("use_testing", "Testing (pytest + default tests)"),
    ("use_ci", "CI pipeline"),
)

DEFAULT_FEATURES: frozenset[str] = frozenset(
    {"use_jwt", "use_testing", "use_code_style"}
)

PRE_COMMIT_OPTIONS: tuple[tuple[str, str], ...] = (
    ("precommit_base", "File hygiene (whitespace, EOF, JSON/YAML, merge conflicts, …)"),
    ("precommit_pyupgrade", "pyupgrade — modern Python syntax"),
    ("precommit_ruff", "Ruff — lint and format"),
    ("precommit_pydoclint", "pydoclint — Google-style docstrings"),
    ("precommit_translation_lint", "django-translation-lint — lowercase gettext strings"),
)

DEFAULT_PRE_COMMIT: frozenset[str] = frozenset(key for key, _ in PRE_COMMIT_OPTIONS)

POSTGRES_VERSIONS: tuple[tuple[str, str], ...] = (
    ("17.10", "PostgreSQL 17.10"),
    ("16.8", "PostgreSQL 16.8"),
    ("15.12", "PostgreSQL 15.12"),
    ("14.17", "PostgreSQL 14.17"),
)

# Must stay in sync with list choices in cookiecutter.json.
# Values returned by the UI / passed as extra_context must be members of these sets.
CHOICE_OPTIONS: dict[str, tuple[str, ...]] = {
    "license": ("MIT", "BEER", "None"),
    "postgres_version": ("17.10", "16.8", "15.12", "14.17"),
    "use_jwt": ("y", "n"),
    "use_sentry": ("y", "n"),
    "use_vscode": ("y", "n"),
    "use_pgadmin": ("y", "n"),
    "use_redis": ("y", "n"),
    "use_rabbitmq": ("y", "n"),
    "use_celery": ("y", "n"),
    "celery_broker": ("redis", "rabbitmq"),
    "use_asgi": ("y", "n"),
    "use_websockets": ("y", "n"),
    "reverse_proxy": ("none", "nginx", "traefik"),
    "use_code_style": ("y", "n"),
    "use_testing": ("y", "n"),
    "use_ci": ("y", "n"),
    "ci_provider": ("github", "gitlab"),
    "precommit_base": ("y", "n"),
    "precommit_pyupgrade": ("y", "n"),
    "precommit_ruff": ("y", "n"),
    "precommit_pydoclint": ("y", "n"),
    "precommit_translation_lint": ("y", "n"),
}


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


def format_precommit_summary(selected_keys: set[str]) -> str:
    enabled = [label for key, label in PRE_COMMIT_OPTIONS if key in selected_keys]
    if not enabled:
        return "none"
    return ", ".join(enabled)


def prompt_yn(label: str, default: str = "y") -> str:
    print(f"  {COLORS.bold}{label}{COLORS.reset}")
    print(
        f"  {COLORS.dim}›{COLORS.reset} "
        f"[{COLORS.green}{default}{COLORS.reset}] (y/n): ",
        end="",
    )
    sys.stdout.flush()

    value = input().strip().lower()
    if not value:
        return default
    if value in ("y", "yes"):
        return "y"
    if value in ("n", "no"):
        return "n"
    return default


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
    postgres_version = prompt_radio(
        "PostgreSQL version",
        "Docker image tag for the Postgres service.",
        POSTGRES_VERSIONS,
        default_index=0,
    )

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
    use_asgi = yn(selected_features, "use_asgi")
    use_websockets = yn(selected_features, "use_websockets")
    use_code_style = yn(selected_features, "use_code_style")
    use_testing = yn(selected_features, "use_testing")
    use_ci = yn(selected_features, "use_ci")

    celery_broker = "redis"
    if use_celery == "y":
        print_section("Celery broker")
        celery_broker = prompt_radio(
            "Celery broker",
            "Message broker for Celery worker and beat.",
            (
                ("redis", "Redis (also enables Redis if needed)"),
                ("rabbitmq", "RabbitMQ (also enables RabbitMQ if needed)"),
            ),
            default_index=0,
        )
        if celery_broker == "redis" and use_redis != "y":
            print(
                f"  {COLORS.yellow}↳ Celery broker is Redis — Redis will be enabled.{COLORS.reset}"
            )
            use_redis = "y"
            selected_features.add("use_redis")
        if celery_broker == "rabbitmq" and use_rabbitmq != "y":
            print(
                f"  {COLORS.yellow}↳ Celery broker is RabbitMQ — RabbitMQ will be enabled.{COLORS.reset}"
            )
            use_rabbitmq = "y"
            selected_features.add("use_rabbitmq")

    if use_websockets == "y":
        if use_asgi != "y":
            print(
                f"  {COLORS.yellow}↳ WebSockets require ASGI — ASGI will be enabled.{COLORS.reset}"
            )
            use_asgi = "y"
            selected_features.add("use_asgi")
        if use_redis != "y":
            print(
                f"  {COLORS.yellow}↳ WebSockets require Redis — Redis will be enabled.{COLORS.reset}"
            )
            use_redis = "y"
            selected_features.add("use_redis")

    print_section("Production reverse proxy")
    reverse_proxy = prompt_radio(
        "Reverse proxy",
        "Optional TLS-ready front proxy for production Compose.",
        (
            ("none", "None — expose the app port directly"),
            ("nginx", "Nginx"),
            ("traefik", "Traefik"),
        ),
        default_index=0,
    )

    ci_provider = "github"
    if use_ci == "y":
        print_section("CI provider")
        ci_provider = prompt_radio(
            "CI provider",
            "Which platform should the pipeline target?",
            (
                ("github", "GitHub Actions (.github/workflows/ci.yml)"),
                ("gitlab", "GitLab CI (.gitlab-ci.yml)"),
            ),
            default_index=0,
        )

    selected_precommit: set[str] = set()
    if use_code_style == "y":
        print_section("Pre-commit hooks")
        selected_precommit = prompt_multiselect(
            "Pre-commit hooks",
            "Choose which checks run on every commit. All recommended; space to toggle.",
            PRE_COMMIT_OPTIONS,
            default_keys=DEFAULT_PRE_COMMIT,
        )
        if not selected_precommit:
            print()
            print(
                f"  {COLORS.yellow}↳ No hooks selected — enabling all pre-commit hooks.{COLORS.reset}"
            )
            selected_precommit = set(DEFAULT_PRE_COMMIT)

    precommit_base = yn(selected_precommit, "precommit_base")
    precommit_pyupgrade = yn(selected_precommit, "precommit_pyupgrade")
    precommit_ruff = yn(selected_precommit, "precommit_ruff")
    precommit_pydoclint = yn(selected_precommit, "precommit_pydoclint")
    precommit_translation_lint = yn(selected_precommit, "precommit_translation_lint")

    print_section("Summary")
    c = COLORS
    print(
        f"  {c.bold}Project{c.reset}     {project_name} {c.dim}({project_slug}){c.reset}"
    )
    print(f"  {c.bold}License{c.reset}     {license_choice}")
    print(f"  {c.bold}Postgres{c.reset}    {postgres_version}")
    print(
        f"  {c.bold}Features{c.reset}    {format_feature_summary(selected_features)}"
    )
    if use_celery == "y":
        print(f"  {c.bold}Celery{c.reset}      broker={celery_broker}")
    print(f"  {c.bold}Proxy{c.reset}       {reverse_proxy}")
    auth_mode = "JWT" if use_jwt == "y" else "session"
    print(f"  {c.bold}Auth{c.reset}        {auth_mode}")
    if use_ci == "y":
        provider_label = "GitHub Actions" if ci_provider == "github" else "GitLab CI"
        print(f"  {c.bold}CI{c.reset}          {provider_label}")
    if use_code_style == "y":
        print(
            f"  {c.bold}Pre-commit{c.reset}  {format_precommit_summary(selected_precommit)}"
        )
    print()

    confirm = prompt_yn("Generate project?", "y")
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
        "postgres_version": postgres_version,
        "use_jwt": use_jwt,
        "use_sentry": use_sentry,
        "use_vscode": use_vscode,
        "use_pgadmin": use_pgadmin,
        "use_redis": use_redis,
        "use_rabbitmq": use_rabbitmq,
        "use_celery": use_celery,
        # Always a valid choice — ignored by templates when Celery is off.
        "celery_broker": celery_broker,
        "use_asgi": use_asgi,
        "use_websockets": use_websockets,
        "reverse_proxy": reverse_proxy,
        "use_code_style": use_code_style,
        "use_testing": use_testing,
        "use_ci": use_ci,
        # Always a valid choice — ignored by post_gen when CI is off.
        "ci_provider": ci_provider,
        "precommit_base": precommit_base if use_code_style == "y" else "n",
        "precommit_pyupgrade": precommit_pyupgrade if use_code_style == "y" else "n",
        "precommit_ruff": precommit_ruff if use_code_style == "y" else "n",
        "precommit_pydoclint": precommit_pydoclint if use_code_style == "y" else "n",
        "precommit_translation_lint": (
            precommit_translation_lint if use_code_style == "y" else "n"
        ),
    }


def validate_choice_answers(answers: dict[str, str]) -> dict[str, str]:
    """Ensure every choice field is a value cookiecutter will accept.

    Cookiecutter raises ``ValueError`` when ``extra_context`` supplies a value
    that is not in the list defined in ``cookiecutter.json`` (e.g. ``ci_provider=none``).
    """
    validated = dict(answers)
    errors: list[str] = []
    for key, options in CHOICE_OPTIONS.items():
        value = validated.get(key)
        if value is None:
            validated[key] = options[0]
            continue
        if value not in options:
            errors.append(f"{key}={value!r} not in {list(options)}")
    if errors:
        raise ValueError(
            "Invalid cookiecutter choice value(s):\n  - " + "\n  - ".join(errors)
        )
    return validated


def generate_project(repo_dir: str, output_dir: str, answers: dict[str, str]) -> None:
    """Generate the project with cookiecutter, skipping this hook's UI tip."""
    os.environ["DSG_COOKIECUTTER_SKIP_PROMPT_UI"] = "1"

    from cookiecutter.main import cookiecutter

    answers = validate_choice_answers(answers)

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
