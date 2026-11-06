import re
import sys

celery = "{{ cookiecutter.use_celery }}"
rabbitmq = "{{ cookiecutter.use_rabbitmq }}"
redis = "{{ cookiecutter.use_redis }}"
celery_broker = "{{ cookiecutter.celery_broker }}"
use_ci = "{{ cookiecutter.use_ci }}"
ci_provider = "{{ cookiecutter.ci_provider }}"
use_asgi = "{{ cookiecutter.use_asgi }}"
use_websockets = "{{ cookiecutter.use_websockets }}"
use_otp_login = "{{ cookiecutter.use_otp_login }}"
use_scoped_apis = "{{ cookiecutter.use_scoped_apis }}"
api_scopes = "{{ cookiecutter.api_scopes }}"
reverse_proxy = "{{ cookiecutter.reverse_proxy }}"
postgres_version = "{{ cookiecutter.postgres_version }}"
project_slug = "{{ cookiecutter.project_slug }}"
use_code_style = "{{ cookiecutter.use_code_style }}"
precommit_base = "{{ cookiecutter.precommit_base }}"
precommit_pyupgrade = "{{ cookiecutter.precommit_pyupgrade }}"
precommit_ruff = "{{ cookiecutter.precommit_ruff }}"
precommit_pydoclint = "{{ cookiecutter.precommit_pydoclint }}"
precommit_translation_lint = "{{ cookiecutter.precommit_translation_lint }}"


def fail(message: str) -> None:
    print()
    print(f"  ERROR: {message}")
    print()
    sys.exit(1)


def slugify(value: str) -> str:
    # Keep in sync with hooks/project_slug.py (this file runs from a temp path).
    slug = value.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    return slug.strip("_")


if not re.match(r"^[_a-zA-Z][_a-zA-Z0-9]+$", project_slug):
    suggested = slugify(project_slug) or slugify("{{ cookiecutter.project_name }}")
    hint = f" Suggested: '{suggested}'." if suggested else ""
    fail(
        f"project_slug '{project_slug}' is invalid. "
        "Use a valid Python package name (letters, numbers, underscore)."
        + hint
    )

if not re.match(r"^\d+(\.\d+)*$", postgres_version):
    fail(
        f"postgres_version '{postgres_version}' is invalid. "
        "Use a Docker tag like 17.10, 16.8, or 15."
    )

if reverse_proxy not in ("none", "nginx", "traefik"):
    fail("reverse_proxy must be 'none', 'nginx', or 'traefik'.")

if use_ci == "y" and ci_provider not in ("github", "gitlab"):
    fail("CI is enabled but ci_provider is invalid. Use 'github' or 'gitlab'.")

if use_websockets == "y" and use_asgi != "y":
    fail("WebSockets require ASGI. Set use_asgi=y or use_websockets=n.")

if use_websockets == "y" and redis != "y":
    fail("WebSockets require Redis for the channel layer. Set use_redis=y.")

if use_otp_login == "y" and redis != "y":
    fail(
        "Phone OTP requires Redis so OTP challenges are shared across workers. "
        "Set use_redis=y (or enable Redis in the feature checklist)."
    )

if use_scoped_apis == "y":
    # Keep validation in sync with hooks/scopes.py (this file runs from a temp path).
    scope_re = re.compile(r"^[a-z][a-z0-9_]*$")
    reserved = {
        "api",
        "v1",
        "docs",
        "schema",
        "static",
        "media",
        "health",
        "i18n",
        "auth",
        "users",
        "files",
    }
    scopes: list[str] = []
    seen: set[str] = set()
    for part in (api_scopes or "").split(","):
        name = part.strip().lower()
        if not name:
            continue
        if name in seen:
            continue
        seen.add(name)
        scopes.append(name)
    if not scopes:
        fail(
            "Multi-scope APIs require api_scopes "
            "(e.g. admin,factory,customer)."
        )
    for name in scopes:
        if not scope_re.match(name):
            fail(
                f"Invalid API scope {name!r}. Use lowercase English letters, "
                "digits, underscore; start with a letter; no spaces."
            )
        if name in reserved:
            fail(f"API scope {name!r} is reserved for platform routes.")

if celery == "y":
    if celery_broker not in ("redis", "rabbitmq"):
        fail("celery_broker must be 'redis' or 'rabbitmq' when Celery is enabled.")
    if celery_broker == "rabbitmq" and rabbitmq != "y":
        fail("Celery broker is RabbitMQ but use_rabbitmq=n. Enable RabbitMQ.")
    if celery_broker == "redis" and redis != "y":
        fail("Celery broker is Redis but use_redis=n. Enable Redis.")

if use_code_style == "y":
    precommit_hooks = (
        precommit_base,
        precommit_pyupgrade,
        precommit_ruff,
        precommit_pydoclint,
        precommit_translation_lint,
    )
    if all(flag == "n" for flag in precommit_hooks):
        fail(
            "Code style is enabled but no pre-commit hooks are selected. "
            "Set at least one precommit_*=y, or set use_code_style=n."
        )
