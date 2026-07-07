# Django Style Guide Cookiecutter

A [Cookiecutter](https://github.com/cookiecutter/cookiecutter) template for Django REST API projects, based on the [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide).

Production deployment uses **Docker Compose on your own server** — not Heroku or other third-party PaaS.

## Features

- Modular `config/settings/` layout (thin `config/django/base.py` aggregator)
- Django REST Framework + drf-spectacular (OpenAPI)
- Docker Compose for local infrastructure and production deployment
- Optional JWT auth, Celery, Redis, RabbitMQ, Sentry, pgAdmin, VS Code, and Ruff/pre-commit
- `python manage.py devserver` — migrate, create superuser, runserver, and optional Celery worker
- `scripts/update_translations.sh` — i18n workflow with `makemessages`
- `start-dev-services.sh` — one command to start dev Docker services

## Prerequisites

- Python 3.10
- [Cookiecutter](https://cookiecutter.readthedocs.io/)
- [Docker](https://www.docker.com/) (for Postgres and optional services)

```bash
pip install cookiecutter
```

## Generate a project

### Interactive (recommended)

```bash
git clone https://github.com/alidanial7/django_style_guide.git
cd django_style_guide
./init.sh
```

Or from anywhere:

```bash
cookiecutter https://github.com/alidanial7/django_style_guide.git
```

### Non-interactive

```bash
cookiecutter https://github.com/alidanial7/django_style_guide.git --no-input \
  project_name="My Project" \
  use_jwt=y \
  use_redis=y \
  use_rabbitmq=y \
  use_celery=y
```

## Configuration options

| Option | Default | Description |
|--------|---------|-------------|
| `project_name` | MyProject | Human-readable project name |
| `project_slug` | auto | Python package name (derived from project name) |
| `license` | MIT | MIT, BEER, or None |
| `postgres_user` / `postgres_password` | user / password | Local Postgres credentials |
| `use_jwt` | y | JWT auth with users + authentication apps |
| `use_sentry` | n | Sentry SDK (activates only when `SENTRY_DSN` is set) |
| `use_vscode` | n | VS Code settings and extension recommendations |
| `use_pgadmin` | n | pgAdmin in dev Docker Compose (`:5050`) |
| `use_redis` | n | Redis cache + dev Docker service |
| `use_rabbitmq` | n | RabbitMQ message broker in Docker Compose |
| `use_celery` | n | Celery worker + beat (**requires RabbitMQ**) |
| `use_code_style` | n | Ruff + pre-commit hooks (replaces flake8-only setup) |

### Dependencies between options

- **Celery → RabbitMQ**: if you enable Celery, RabbitMQ must be enabled too. Generation fails with a clear message otherwise.
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
│   └── users/               # when use_jwt=y
├── docker/                  # Dockerfiles and entrypoints
├── docker-compose.yml       # production stack
├── docker-compose.dev.yml   # local infrastructure
├── start-dev-services.sh
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
python3.10 -m venv venv && source venv/bin/activate
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
