"""Interactive terminal UI for the Django Style Guide cookiecutter."""

from __future__ import annotations

import os
import select
import shutil
import sys
import tempfile
import termios
import tty
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path

# Allowed when generating into an existing directory (inplace).
_GIT_ONLY_ENTRIES = frozenset({
    ".git",
    ".gitignore",
    ".gitattributes",
    ".gitmodules",
})

# Signals "this cwd is the cookiecutter template", not a blank app repo.
_TEMPLATE_ROOT_MARKERS = frozenset({
    "cookiecutter.json",
    "{{cookiecutter.project_name}}",
})

_HOOKS_DIR = Path(__file__).resolve().parent
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))

from project_slug import slugify  # noqa: E402


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
            f"{self.dim}  ↑↓ / jk move  ·  space select  ·  enter confirm{self.reset}"
        )
        self.multiselect_hint = (
            f"{self.dim}  ↑↓ / jk move  ·  space toggle  ·  enter confirm{self.reset}"
        )


COLORS = _Colors()

FEATURE_OPTIONS: tuple[tuple[str, str], ...] = (
    ("use_jwt", "JWT authentication (off = session auth)"),
    ("use_otp_login", "Phone OTP login (SMS provider stub)"),
    ("use_google_login", "Google social login (id_token)"),
    ("use_microsoft_login", "Microsoft social login (id_token)"),
    ("use_apple_login", "Apple social login (id_token)"),
    ("use_i18n", "Django i18n / multi-language (LocaleMiddleware + locales)"),
    ("use_uuid_pk", "UUID primary keys for models (off = BigAutoField)"),
    ("use_scoped_apis", "Multi-scope APIs (/api/v1/<scope>/… + /api/docs/<scope>/)"),
    ("use_file_manager", "ManagedFile file_manager app"),
    ("use_unfold_admin", "Django Unfold admin UI"),
    ("use_portal_permissions", "Portal permission stubs (IsAdmin / IsCustomer; unused when multi-scope)"),
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
    {"use_jwt", "use_uuid_pk", "use_testing", "use_code_style"}
)

PRE_COMMIT_OPTIONS: tuple[tuple[str, str], ...] = (
    ("precommit_base", "File hygiene (whitespace, EOF, JSON/YAML, merge conflicts, …)"),
    ("precommit_pyupgrade", "pyupgrade — modern Python syntax"),
    ("precommit_ruff", "Ruff — lint and format"),
    ("precommit_pydoclint", "pydoclint — Google-style docstrings"),
    (
        "precommit_translation_lint",
        "django-translation-lint — lowercase gettext strings",
    ),
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
    "user_login_field": ("email", "username"),
    "use_otp_login": ("y", "n"),
    "use_google_login": ("y", "n"),
    "use_microsoft_login": ("y", "n"),
    "use_apple_login": ("y", "n"),
    "use_i18n": ("y", "n"),
    "use_uuid_pk": ("y", "n"),
    "use_scoped_apis": ("y", "n"),
    "use_file_manager": ("y", "n"),
    "use_unfold_admin": ("y", "n"),
    "use_portal_permissions": ("y", "n"),
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


def _cursor_up(lines: int) -> None:
    if lines <= 0:
        return
    sys.stdout.write(f"\033[{lines}A")
    sys.stdout.flush()


@contextmanager
def _cbreak_terminal() -> Iterator[int]:
    """Keep stdin in cbreak for the whole prompt so IDE terminals don't steal ↑↓.

    Toggling cooked mode after every key lets Cursor/VS Code bind arrows to
    scrollback. ``setcbreak`` (not ``setraw``) still delivers keys immediately
    but keeps output post-processing so ``print()`` newlines render correctly.
    Prefer ``os.read`` over ``sys.stdin.read`` so ``select`` matches the fd.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        # Application cursor keys: ↑↓ → ESC O A / ESC O B (in addition to CSI).
        sys.stdout.write("\033[?1h")
        sys.stdout.flush()
        yield fd
    finally:
        sys.stdout.write("\033[?1l")
        sys.stdout.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def _read_byte(fd: int) -> str:
    data = os.read(fd, 1)
    if not data:
        return ""
    return data.decode("latin-1")


def _read_escape_sequence(fd: int, first: str = "\x1b") -> str:
    """Read a full CSI/SS3 sequence after ESC (arrows, etc.)."""
    key = first
    # IDE PTYs sometimes deliver follow-up bytes slowly.
    r, _, _ = select.select([fd], [], [], 0.35)
    if not r:
        return key

    while True:
        ch = _read_byte(fd)
        if not ch:
            break
        key += ch
        if len(key) == 2 and ch not in ("[", "O"):
            break
        # CSI/SS3 final byte is in the @–~ range (arrows end with A/B/C/D).
        if len(key) >= 3 and "@" <= ch <= "~":
            break
        r, _, _ = select.select([fd], [], [], 0.05)
        if not r:
            break

    return key


def _normalize_nav_key(key: str) -> str:
    """Map raw terminal bytes to stable nav tokens: up/down/space/enter/other."""
    if key in ("\x1b[A", "\x1bOA", "k", "K", "w", "W"):
        return "up"
    if key in ("\x1b[B", "\x1bOB", "j", "J", "s", "S"):
        return "down"
    if key == " ":
        return "space"
    if key in ("\r", "\n"):
        return "enter"
    # Modified / extended arrows still end with A/B.
    if len(key) >= 3 and key.startswith("\x1b") and key[-1] == "A":
        return "up"
    if len(key) >= 3 and key.startswith("\x1b") and key[-1] == "B":
        return "down"
    return key


def _read_key(fd: int) -> str:
    key = _read_byte(fd)
    if key == "\x03":
        raise KeyboardInterrupt
    if key == "\x1b":
        key = _read_escape_sequence(fd, key)
    normalized = _normalize_nav_key(key)
    if os.environ.get("DSG_DEBUG_KEYS"):
        sys.stderr.write(f"[dsg-keys] raw={key!r} -> {normalized!r}\n")
        sys.stderr.flush()
    return normalized


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
        with _cbreak_terminal() as fd:
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
                    print(f"  {pointer} {style}({marker}) {label}{COLORS.reset}")

                print()
                print(COLORS.radio_hint)

                redraw = True
                key = _read_key(fd)

                if key == "up":
                    focus = max(0, focus - 1)
                elif key == "down":
                    focus = min(count - 1, focus + 1)
                elif key == "space":
                    selected = focus
                elif key == "enter":
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
        with _cbreak_terminal() as fd:
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
                key = _read_key(fd)

                if key == "up":
                    focus = max(0, focus - 1)
                elif key == "down":
                    focus = min(count - 1, focus + 1)
                elif key == "space":
                    option_key = options[focus][0]
                    if option_key in selected:
                        selected.remove(option_key)
                    else:
                        selected.add(option_key)
                elif key == "enter":
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


def list_non_git_entries(target: Path) -> list[str]:
    """Return names of entries that are not plain git metadata."""
    if not target.exists():
        return []
    return sorted(
        entry.name for entry in target.iterdir() if entry.name not in _GIT_ONLY_ENTRIES
    )


def is_cookiecutter_template_root(target: Path) -> bool:
    """True when *target* looks like this template (not an empty app repo)."""
    names = {entry.name for entry in target.iterdir()} if target.is_dir() else set()
    return _TEMPLATE_ROOT_MARKERS.issubset(names)


def assert_inplace_target_ok(target: Path) -> None:
    """Fail if *target* has anything beyond git metadata files/dirs."""
    offenders = list_non_git_entries(target)
    if not offenders:
        return
    listed = "\n".join(f"  - {name}" for name in offenders)
    raise ValueError(
        "Cannot generate inplace: directory has non-git files:\n"
        f"{listed}\n"
        "Remove them, pass --inplace-force / answer Yes to force-clean, "
        "or generate into a new folder."
    )


def clean_inplace_target(target: Path) -> list[str]:
    """Delete everything except git metadata. Returns removed entry names."""
    removed: list[str] = []
    for entry in sorted(target.iterdir(), key=lambda p: p.name):
        if entry.name in _GIT_ONLY_ENTRIES:
            continue
        if entry.is_dir() and not entry.is_symlink():
            shutil.rmtree(entry)
        else:
            entry.unlink()
        removed.append(entry.name)
    return removed


def _copy_template_snapshot(repo_dir: Path) -> Path:
    """Copy template to a temp dir so cwd can be force-cleaned safely."""
    ignore = shutil.ignore_patterns(
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "_gen_smoke",
        "*.pyc",
        ".DS_Store",
    )
    snapshot = Path(tempfile.mkdtemp(prefix="dsg-template-"))
    # copytree into snapshot/contents — put files directly in snapshot
    for item in repo_dir.iterdir():
        if item.name in {".git", ".venv", "venv", "_gen_smoke"}:
            continue
        dest = snapshot / item.name
        if item.is_dir():
            shutil.copytree(item, dest, ignore=ignore)
        elif item.is_file():
            shutil.copy2(item, dest)
    return snapshot


def flatten_generated_project(output_dir: Path, project_name: str) -> None:
    """Move ``output_dir/project_name/*`` up into ``output_dir`` and remove the folder.

    Renames the cookiecutter folder to a unique staging name first so a package
    named the same as ``project_name`` (common when slug == name) does not
    collide with the parent directory being emptied.
    """
    generated = output_dir / project_name
    if not generated.is_dir():
        raise RuntimeError(f"Expected generated project at {generated}")

    staging = output_dir / f".dsg_inplace_{os.getpid()}"
    if staging.exists():
        shutil.rmtree(staging)
    generated.rename(staging)

    try:
        for item in list(staging.iterdir()):
            dest = output_dir / item.name
            if dest.exists():
                if dest.name == ".git":
                    # Never replace the existing repo metadata.
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                    continue
                if dest.name in _GIT_ONLY_ENTRIES:
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                else:
                    raise RuntimeError(
                        f"Refusing to overwrite unexpected path during inplace move: {dest}"
                    )
            shutil.move(str(item), str(dest))
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)


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
            f"  {COLORS.dim}›{COLORS.reset} [{COLORS.green}{default}{COLORS.reset}]: ",
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


def _collect_answers_impl() -> dict[str, str] | None:
    """Run the interactive wizard. Returns None when the user cancels."""
    print_banner()

    print_section("Project")
    project_name = prompt_text("Project name", "MyProject")
    default_slug = slugify(project_name)
    project_slug = (
        prompt_text("Project slug (Python package)", default_slug) or default_slug
    )

    print_section("Output location")
    cwd = Path.cwd()
    force_inplace = os.environ.get("DSG_INPLACE") == "1"
    force_clean = os.environ.get("DSG_INPLACE_FORCE") == "1"
    force_template = os.environ.get("DSG_INPLACE_FORCE_TEMPLATE") == "1"
    inplace_force = "n"
    inplace_force_template = "n"

    if force_inplace or force_clean or force_template:
        inplace = "y"
        if force_template:
            flag = "--inplace-force-template"
        elif force_clean:
            flag = "--inplace-force"
        else:
            flag = "--inplace"
        print(
            f"  {COLORS.dim}↳ {flag} — will generate into the current directory"
            f"{' (force-clean non-git files)' if force_clean or force_template else ''}"
            f"{COLORS.reset}"
        )
    else:
        inplace = prompt_yn(
            "Generate into the current directory (existing git repo)?",
            "n",
        )

    if inplace == "y":
        offenders = list_non_git_entries(cwd)
        if not offenders:
            print(
                f"  {COLORS.green}↳ Current directory is git-only (or empty) — "
                f"OK for inplace.{COLORS.reset}"
            )
        else:
            listed = "\n".join(f"    - {name}" for name in offenders)
            print()
            print(
                f"  {COLORS.yellow}Directory has non-git files that must be removed "
                f"for inplace:{COLORS.reset}\n{listed}"
            )
            template_root = is_cookiecutter_template_root(cwd)
            if template_root:
                print(
                    f"  {COLORS.yellow}↳ This looks like the cookiecutter template itself. "
                    f"Force-clean is destructive — requires --inplace-force-template "
                    f"(or type FORCE below).{COLORS.reset}"
                )
            if force_template:
                inplace_force = "y"
                inplace_force_template = "y"
                print(
                    f"  {COLORS.dim}↳ DSG_INPLACE_FORCE_TEMPLATE=1 — will snapshot, "
                    f"delete non-git files, then generate.{COLORS.reset}"
                )
            elif force_clean:
                if template_root:
                    print(
                        f"  {COLORS.yellow}Refusing --inplace-force on the template repo. "
                        f"Use --inplace-force-template if you really mean it.{COLORS.reset}"
                    )
                    return None
                inplace_force = "y"
                print(
                    f"  {COLORS.dim}↳ DSG_INPLACE_FORCE=1 — will delete the files above "
                    f"before generating.{COLORS.reset}"
                )
            else:
                inplace_force = prompt_yn(
                    "Force-delete those files and generate here?",
                    "n",
                )
                if inplace_force != "y":
                    print(f"  {COLORS.dim}Cancelled.{COLORS.reset}")
                    return None
                if template_root:
                    typed = prompt_text(
                        "Type FORCE to replace this cookiecutter template",
                        "",
                    ).strip()
                    if typed != "FORCE":
                        print(
                            f"  {COLORS.dim}Cancelled "
                            f"(expected FORCE, got {typed!r}).{COLORS.reset}"
                        )
                        return None
                    inplace_force_template = "y"
                print(
                    f"  {COLORS.green}↳ Will force-clean then generate inplace.{COLORS.reset}"
                )

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
    use_otp_login = yn(selected_features, "use_otp_login")
    use_google_login = yn(selected_features, "use_google_login")
    use_microsoft_login = yn(selected_features, "use_microsoft_login")
    use_apple_login = yn(selected_features, "use_apple_login")
    use_i18n = yn(selected_features, "use_i18n")

    print_section("Login identifier")
    user_login_field = prompt_radio(
        "Login with",
        "Primary credential clients send on login/register (USERNAME_FIELD).",
        (
            ("email", "Email + password"),
            ("username", "Username + password (email still stored for reset/notify)"),
        ),
        default_index=0,
    )

    use_uuid_pk = yn(selected_features, "use_uuid_pk")
    use_scoped_apis = yn(selected_features, "use_scoped_apis")
    use_file_manager = yn(selected_features, "use_file_manager")
    use_unfold_admin = yn(selected_features, "use_unfold_admin")
    use_portal_permissions = yn(selected_features, "use_portal_permissions")
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

    api_scopes = "admin,factory"
    if use_scoped_apis == "y":
        print_section("API scopes")
        from scopes import parse_api_scopes, validate_api_scopes

        while True:
            api_scopes = prompt_text(
                "Scopes (comma-separated)",
                "admin,factory",
            ).strip()
            print(
                f"  {COLORS.dim}Example: admin,factory,customer — lowercase English, "
                f"no spaces; used in /api/v1/<scope>/ and model names.{COLORS.reset}"
            )
            try:
                validate_api_scopes(parse_api_scopes(api_scopes))
                break
            except ValueError as error:
                print(f"  {COLORS.yellow}{error}{COLORS.reset}")
        if use_portal_permissions == "y":
            print(
                f"  {COLORS.dim}↳ Multi-scope generates Is<Scope>User permissions; "
                f"legacy IsAdmin/IsCustomer stubs are skipped.{COLORS.reset}"
            )
    else:
        api_scopes = ""

    print_section("Infra alerts")
    infra_repo_name = prompt_text(
        "Infra repo name (optional)",
        "",
    ).strip()

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

    if use_otp_login == "y" and use_redis != "y":
        print(
            f"  {COLORS.yellow}↳ Phone OTP requires Redis for shared challenges — "
            f"Redis will be enabled.{COLORS.reset}"
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
    print(f"  {c.bold}Features{c.reset}    {format_feature_summary(selected_features)}")
    if use_celery == "y":
        print(f"  {c.bold}Celery{c.reset}      broker={celery_broker}")
    print(f"  {c.bold}Proxy{c.reset}       {reverse_proxy}")
    pk_type = "UUID" if use_uuid_pk == "y" else "BigAutoField"
    print(f"  {c.bold}Primary Key{c.reset} {pk_type}")
    auth_mode = "JWT" if use_jwt == "y" else "session"
    otp_label = " · OTP phone" if use_otp_login == "y" else ""
    social_bits = [
        name
        for flag, name in (
            (use_google_login, "Google"),
            (use_microsoft_login, "Microsoft"),
            (use_apple_login, "Apple"),
        )
        if flag == "y"
    ]
    social_label = f" · social={'+'.join(social_bits)}" if social_bits else ""
    print(
        f"  {c.bold}Auth{c.reset}        {auth_mode} · login={user_login_field}"
        f"{otp_label}{social_label}"
    )
    output_label = f"./{project_name}/"
    if inplace == "y":
        output_label = (
            "current directory (inplace, force-clean)"
            if inplace_force == "y"
            else "current directory (inplace)"
        )
    print(f"  {c.bold}Output{c.reset}      {output_label}")
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
        "_inplace": inplace,
        "_inplace_force": inplace_force,
        "_inplace_force_template": inplace_force_template,
        "project_name": project_name,
        "project_slug": project_slug,
        "first_name": first_name,
        "last_name": last_name,
        "license": license_choice,
        "postgres_user": postgres_user,
        "postgres_password": postgres_password,
        "postgres_version": postgres_version,
        "use_jwt": use_jwt,
        "user_login_field": user_login_field,
        "use_otp_login": use_otp_login,
        "use_google_login": use_google_login,
        "use_microsoft_login": use_microsoft_login,
        "use_apple_login": use_apple_login,
        "use_i18n": use_i18n,
        "use_uuid_pk": use_uuid_pk,
        "use_scoped_apis": use_scoped_apis,
        "api_scopes": api_scopes,
        "use_file_manager": use_file_manager,
        "use_unfold_admin": use_unfold_admin,
        "use_portal_permissions": use_portal_permissions,
        "infra_repo_name": infra_repo_name,
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


def collect_answers() -> dict[str, str] | None:
    """Run the interactive wizard with graceful cancellation on Ctrl+C."""
    try:
        return _collect_answers_impl()
    except KeyboardInterrupt:
        print(f"\n  {COLORS.dim}Cancelled.{COLORS.reset}")
        return None


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

    inplace = answers.pop("_inplace", "n") == "y"
    inplace_force = answers.pop("_inplace_force", "n") == "y"
    inplace_force_template = (
        answers.pop("_inplace_force_template", "n") == "y"
        or os.environ.get("DSG_INPLACE_FORCE_TEMPLATE") == "1"
    )
    answers = validate_choice_answers(answers)
    target = Path(output_dir).resolve()
    template_src = Path(repo_dir).resolve()
    template_for_cookiecutter = str(template_src)
    snapshot: Path | None = None

    c = COLORS
    try:
        if inplace:
            offenders = list_non_git_entries(target)
            if offenders and not inplace_force:
                assert_inplace_target_ok(target)
            if offenders and inplace_force:
                cleaning_template = (
                    is_cookiecutter_template_root(target)
                    or template_src == target
                    or template_src.is_relative_to(target)
                )
                if cleaning_template and not inplace_force_template:
                    raise ValueError(
                        "Refusing to force-clean a cookiecutter template root. "
                        "Pass --inplace-force-template (or DSG_INPLACE_FORCE_TEMPLATE=1) "
                        "if you intentionally want to replace the template with a "
                        "generated app."
                    )
                # Cleaning cwd would delete the template if it lives here — snapshot first.
                if cleaning_template:
                    print(
                        f"  {c.dim}↳ Snapshotting template aside before force-clean…{c.reset}"
                    )
                    snapshot = _copy_template_snapshot(template_src)
                    template_for_cookiecutter = str(snapshot)
                print(f"  {c.dim}↳ Force-cleaning non-git files in {target}…{c.reset}")
                removed = clean_inplace_target(target)
                for name in removed:
                    print(f"  {c.dim}  - removed {name}{c.reset}")

        print()
        print(f"{c.cyan}{c.bold}  Generating project...{c.reset}")
        print()

        cookiecutter(
            template_for_cookiecutter,
            no_input=True,
            extra_context=answers,
            output_dir=str(target),
            accept_hooks=True,
            overwrite_if_exists=False,
        )

        project_name = answers["project_name"]
        if inplace:
            flatten_generated_project(target, project_name)
            print()
            print(
                f"{c.green}{c.bold}  ✓ Done!{c.reset}  "
                f"{c.dim}files are in {target} — see README.md{c.reset}"
            )
            print()
            return

        print()
        print(
            f"{c.green}{c.bold}  ✓ Done!{c.reset}  "
            f"{c.dim}cd {project_name} && see README.md{c.reset}"
        )
        print()
    finally:
        if snapshot is not None and snapshot.exists():
            shutil.rmtree(snapshot, ignore_errors=True)


def run_cli(repo_dir: str) -> int:
    """Entry point for init.sh and other local wrappers."""
    answers = collect_answers()
    if answers is None:
        return 0

    output_dir = os.environ.get("PWD") or "."
    try:
        generate_project(repo_dir, output_dir, answers)
    except ValueError as error:
        print(f"  {COLORS.yellow}{error}{COLORS.reset}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: interactive_prompts.py <template-directory> "
            "[--inplace|--inplace-force|--inplace-force-template]",
            file=sys.stderr,
        )
        sys.exit(2)
    repo = sys.argv[1]
    flags = set(sys.argv[2:])
    if "--inplace-force-template" in flags:
        os.environ["DSG_INPLACE"] = "1"
        os.environ["DSG_INPLACE_FORCE"] = "1"
        os.environ["DSG_INPLACE_FORCE_TEMPLATE"] = "1"
    elif "--inplace-force" in flags:
        os.environ["DSG_INPLACE"] = "1"
        os.environ["DSG_INPLACE_FORCE"] = "1"
    elif "--inplace" in flags:
        os.environ["DSG_INPLACE"] = "1"
    sys.exit(run_cli(repo))
