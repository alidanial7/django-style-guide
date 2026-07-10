# Django Style Guide Cookiecutter

A [Cookiecutter](https://github.com/cookiecutter/cookiecutter) template for Django REST API projects, based on the [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide).

Production deployment uses **Docker Compose on your own server** — not Heroku or other third-party PaaS.

## Features

- Modular `config/settings/` layout (thin `config/django/base.py` aggregator)
- Django REST Framework + drf-spectacular (OpenAPI)
- Docker Compose for local infrastructure and production deployment
- Optional JWT auth, Celery, Redis, RabbitMQ, Sentry, pgAdmin, VS Code, Ruff/pre-commit, pytest, and CI (GitHub Actions or GitLab CI)
- `python manage.py devserver` — migrate, create superuser, runserver, and optional Celery worker
- `scripts/update_translations.sh` — i18n workflow with `makemessages`
- `start-dev-services.sh` — one command to start dev Docker services

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
cookiecutter https://github.com/alidanial7/django_style_guide.git
```

Requires [cookiecutter 2.4+](https://cookiecutter.readthedocs.io/) (for the `pre_prompt` hook).

The interactive UI uses keyboard-driven prompts:

- **↑ / ↓** — move focus
- **Space** — toggle (features) or select (single-choice)
- **Enter** — confirm

Features are shown as a single checklist — select everything you want in one screen.

When **code style tooling** is enabled, a second checklist lets you pick which **pre-commit hook groups** to include (all selected by default; use Space to deselect any you do not want).

You can also clone the repo and run `./init.sh`, which uses the same UI.

### Non-interactive

```bash
cookiecutter https://github.com/alidanial7/django_style_guide.git --no-input \
  project_name="My Project" \
  use_jwt=y \
  use_redis=y \
  use_rabbitmq=y \
  use_celery=y \
  use_ci=y \
  ci_provider=github
```

## Configuration options

| Option | Default | Description |
|--------|---------|-------------|
| `project_name` | MyProject | Human-readable project name |
| `project_slug` | auto | Python package name (derived from project name) |
| `license` | MIT | MIT, BEER, or None |
| `postgres_user` / `postgres_password` | user / password | Local Postgres credentials |
| `use_jwt` | y | JWT auth with users app (auth + profile + register) |
| `use_sentry` | n | Sentry SDK (activates only when `SENTRY_DSN` is set) |
| `use_vscode` | n | VS Code settings and extension recommendations |
| `use_pgadmin` | n | pgAdmin in dev Docker Compose (`:5050`) |
| `use_redis` | n | Redis cache + dev Docker service |
| `use_rabbitmq` | n | RabbitMQ message broker in Docker Compose |
| `use_celery` | n | Celery worker + beat (**requires RabbitMQ**) |
| `use_code_style` | n | Ruff + pre-commit hooks (replaces flake8-only setup) |
| `use_testing` | y | pytest, factories, and default tests |
| `use_ci` | n | CI pipeline config |
| `ci_provider` | github | `github` (Actions) or `gitlab` (GitLab CI); only when `use_ci=y` |
| `precommit_base` | y | File hygiene hooks (only when `use_code_style=y`) |
| `precommit_pyupgrade` | y | pyupgrade syntax modernizer |
| `precommit_ruff` | y | Ruff lint + format |
| `precommit_pydoclint` | y | Google-style docstring lint |
| `precommit_translation_lint` | y | Django gettext lowercase lint |

When using the interactive UI with code style enabled, hook groups are selected via a multiselect (all on by default). With `--no-input`, all hook groups default to `y` if `use_code_style=y`.

### Pre-commit hook groups (when `use_code_style=y`)

| Group | Purpose |
|-------|---------|
| **File hygiene** | Whitespace, EOF, JSON/YAML/XML, merge conflicts, private keys, AST checks |
| **pyupgrade** | Modern Python 3.12 syntax |
| **Ruff** | Lint (`E`, `F`, `W`, `I`) and format |
| **pydoclint** | Google-style docstrings |
| **django-translation-lint** | Lowercase Django translation strings |

### Dependencies between options

- **Celery → RabbitMQ**: if you enable Celery, RabbitMQ must be enabled too. Generation fails with a clear message otherwise.
- **CI → provider**: if you enable CI, choose **GitHub Actions** or **GitLab CI**. Interactive mode asks after the features checklist; with `--no-input` set `use_ci=y` and `ci_provider=github` or `ci_provider=gitlab`.
- **Redis**, **pgAdmin**, **Sentry**, **VS Code**, and **code style** are independent.

## Project layout (generated)

```
my_project/
├── config/                  # Django project config
│   ├── django/              # base, local, production, test settings
│   ├── settings/            # apps, auth, cache, celery, drf, i18n, ...
│   ├── urls.py
│   ├── celery.py
│   └── tasks.py
├── my_project/              # Application package (project_slug)
│   ├── api/                 # DRF layer
│   ├── core/
│   ├── common/
│   ├── commands/            # devserver management command
│   └── users/               # when use_jwt=y (models/, manager/, selector/, services/, apis/, urls/)
├── docker/                  # Dockerfiles and entrypoints
├── docker-compose.yml       # production stack
├── docker-compose.dev.yml   # local infrastructure
├── start-dev-services.sh
├── .github/workflows/       # when use_ci=y and ci_provider=github
├── .gitlab-ci.yml           # when use_ci=y and ci_provider=gitlab
├── scripts/
│   └── update_translations.sh
└── requirements/
    ├── base.txt
    ├── local.txt
    └── production.txt
```

## After generation

See the generated project's `README.md` for setup steps.

Quick start:

```bash
cd my_project
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements_dev.txt
cp .env.example .env
./start-dev-services.sh    # in another terminal, or run with -d via compose
python manage.py devserver
```

- API docs: `http://localhost:8000/` (Swagger)
- Admin: `http://localhost:8000/admin/`

## Contributing

Issues and pull requests are welcome on [GitHub](https://github.com/alidanial7/django_style_guide).

## License

MIT
