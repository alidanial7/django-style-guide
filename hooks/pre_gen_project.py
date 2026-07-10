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
reverse_proxy = "{{ cookiecutter.reverse_proxy }}"
postgres_version = "{{ cookiecutter.postgres_version }}"
project_slug = "{{ cookiecutter.project_slug }}"


def fail(message: str) -> None:
    print()
    print(f"  ERROR: {message}")
    print()
    sys.exit(1)


if not re.match(r"^[_a-zA-Z][_a-zA-Z0-9]+$", project_slug):
    fail(
        f"project_slug '{project_slug}' is invalid. "
        "Use a valid Python package name (letters, numbers, underscore)."
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

if celery == "y":
    if celery_broker not in ("redis", "rabbitmq"):
        fail("celery_broker must be 'redis' or 'rabbitmq' when Celery is enabled.")
    if celery_broker == "rabbitmq" and rabbitmq != "y":
        fail("Celery broker is RabbitMQ but use_rabbitmq=n. Enable RabbitMQ.")
    if celery_broker == "redis" and redis != "y":
        fail("Celery broker is Redis but use_redis=n. Enable Redis.")
