# Django Style Guide Cookiecutter

A [Cookiecutter](https://github.com/cookiecutter/cookiecutter) template for Django REST API projects, based on the [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide).

Template version: see [`VERSION`](VERSION). Production deployment uses **Docker Compose on your own server** — not Heroku or other third-party PaaS.

> **Repository:** [github.com/alidanial7/django-style-guide](https://github.com/alidanial7/django-style-guide)
>
> Template contributors: start with [`AGENTS.md`](AGENTS.md) and `.cursor/rules/`.

## Features

- Modular `config/settings/` layout (thin `config/django/base.py` aggregator)
- Django REST Framework + drf-spectacular (OpenAPI; Swagger only when `DEBUG=True`)
- Docker Compose for local infrastructure and production deployment
- Optional reverse proxy: **Nginx** or **Traefik**
- Auth: **JWT** or **session** (users app always included)
- Optional Celery with broker choice: **Redis** or **RabbitMQ**
- Optional ASGI (Uvicorn) and Django Channels / WebSockets
- Optional Sentry, Redis, RabbitMQ, pgAdmin, VS Code, Ruff/pre-commit, pytest, CI
- `python manage.py start_domain_app` — HackSoft-style domain scaffolding
- `python manage.py devserver` — migrate, create superuser, runserver, optional Celery
- Generated [`docs/style-guide/`]({{cookiecutter.project_name}}/docs/style-guide/README.md) — deep conventions (open one page at a time)
- Generated [`AGENTS.md`]({{cookiecutter.project_name}}/AGENTS.md) + [`.cursor/rules/`]({{cookiecutter.project_name}}/.cursor/rules/) — slim agent index and glob-scoped rules (feature rules omitted when options are off)

## Prerequisites

- Python 3.12
- [Cookiecutter](https://cookiecutter.readthedocs.io/)
- [Docker](https://www.docker.com/) (for Postgres and optional services)

```bash
pip install "cookiecutter>=2.4"
```

## Generate a project

### Interactive (recommended)

```bash
cookiecutter https://github.com/alidanial7/django-style-guide.git
```

Requires [cookiecutter 2.4+](https://cookiecutter.readthedocs.io/) (for the `pre_prompt` hook).

On a TTY, the checklist UI runs automatically (↑/↓, Space, Enter). After generation the process may exit with code **143** — that is normal (the outer cookiecutter is stopped so you are not prompted twice).

You can also clone and run `./init.sh` for the same UI.

### Minimal preset (recommended defaults)

Interactive UI already defaults to JWT + UUID PK + testing + Ruff. Equivalent `--no-input`:

```bash
cookiecutter https://github.com/alidanial7/django-style-guide.git --no-input \
  project_name="MyProject" \
  use_jwt=y \
  use_uuid_pk=y \
  use_testing=y \
  use_code_style=y \
  use_celery=n \
  use_redis=n \
  use_ci=n \
  reverse_proxy=none
```

### Non-interactive

Prefer the checklist UI (`cookiecutter …` on a TTY or `./init.sh`). Plain `--no-input` still accepts every flag — set Celery/WS/CI deps yourself or `pre_gen` will fail:

```bash
cookiecutter https://github.com/alidanial7/django-style-guide.git --no-input \
  project_name="My Project" \
  use_jwt=y \
  use_redis=y \
  use_celery=y \
  celery_broker=redis \
  reverse_proxy=nginx \
  postgres_version=17.10 \
  use_asgi=n \
  use_websockets=n \
  use_ci=y \
  ci_provider=github \
  precommit_base=y \
  precommit_ruff=y
```

## Configuration options

| Option | Default | Description |
|--------|---------|-------------|
| `project_name` | MyProject | Human-readable project name (output directory) |
| `project_slug` | auto | Python package name (from name; spaces/hyphens/dots → `_`) |
| `first_name` / `last_name` | author / … | Author metadata for LICENSE |
| `license` | MIT | MIT, BEER, or None |
| `postgres_user` / `postgres_password` | user / password | Local Postgres credentials |
| `postgres_version` | 17.10 | Docker Postgres image tag |
| `use_jwt` | y | `y` → JWT; `n` → session auth (users app always kept) |
| `use_uuid_pk` | y | `y` → UUID PK on `BaseModel`; `n` → default `BigAutoField` |
| `use_sentry` | n | Sentry SDK (activates when `SENTRY_DSN` is set) |
| `use_vscode` | n | VS Code settings |
| `use_pgadmin` | n | pgAdmin in dev Compose (`:5050`) |
| `use_redis` | n | Redis cache (+ required for Redis Celery / WebSockets) |
| `use_rabbitmq` | n | RabbitMQ broker |
| `use_celery` | n | Celery worker + beat |
| `celery_broker` | redis | `redis` or `rabbitmq` (when Celery is on) |
| `use_asgi` | n | Uvicorn instead of Gunicorn |
| `use_websockets` | n | Django Channels (requires ASGI + Redis) |
| `reverse_proxy` | none | `none`, `nginx`, or `traefik` |
| `use_code_style` | y | Ruff + pre-commit |
| `precommit_base` | y | File hygiene hooks (when code style is on) |
| `precommit_pyupgrade` | y | pyupgrade hook |
| `precommit_ruff` | y | Ruff lint/format hooks |
| `precommit_pydoclint` | y | pydoclint hook |
| `precommit_translation_lint` | y | django-translation-lint hook |
| `use_testing` | y | pytest + default tests |
| `use_ci` | n | CI pipeline |
| `ci_provider` | github | `github` or `gitlab` |

### Dependencies between options

- **Celery → broker**: Redis broker requires `use_redis=y`; RabbitMQ broker requires `use_rabbitmq=y`.
- **WebSockets → ASGI + Redis**.
- **CI → provider**: `github` or `gitlab` when `use_ci=y`.
- **Code style → hooks**: with `use_code_style=y`, enable at least one `precommit_*=y` (interactive UI defaults all on if you pick none).

## After generation

See the generated project's `README.md` for setup.

Coding conventions and architecture live in the generated project's style guide:

- [`docs/style-guide/README.md`]({{cookiecutter.project_name}}/docs/style-guide/README.md) — index
- Template source in this repo: [`{{cookiecutter.project_name}}/docs/style-guide/`]({{cookiecutter.project_name}}/docs/style-guide/)

Quick start (directory name = `project_name`, e.g. `MyProject`):

```bash
cd MyProject
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements_dev.txt
cp .env.example .env
./start-dev-services.sh
python manage.py devserver
```

## Template CI & local smoke

GitHub Actions: `scripts/smoke_generate.sh` (option/agent-surface asserts) then a generate+pytest matrix (JWT, int PK, session+Celery, RabbitMQ, ASGI+WS, no-testing/GitLab, flake8-only).

```bash
make choices   # cookiecutter.json ↔ UI maps
make smoke     # needs cookiecutter + ripgrep; writes _gen_smoke/
```

## Contributing

Issues and pull requests are welcome on [GitHub](https://github.com/alidanial7/django-style-guide).

## License

MIT
