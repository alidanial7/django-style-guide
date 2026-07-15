# {{cookiecutter.project_name}}

Django REST API project generated from the [Django Style Guide](https://github.com/alidanial7/django-style-guide) cookiecutter.

Based on the [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide).

## Documentation

Conventions, architecture, and how to write code live under **[`docs/style-guide/`](docs/style-guide/README.md)** (source of truth for humans and agents).

Coding agents: start with **[`AGENTS.md`](AGENTS.md)**.

| Start here | Topic |
|------------|--------|
| [Style guide index](docs/style-guide/README.md) | Full table of contents |
| [Architecture](docs/style-guide/overview/architecture.md) | Layers & request flow |
| [Security](docs/style-guide/http/security.md) | Deny-by-default, secrets, DEBUG |
| [Domain apps](docs/style-guide/overview/domain-apps.md) | `start_domain_app` |
| [Validation](docs/style-guide/domain/validation.md) · [Errors](docs/style-guide/domain/errors.md) | Validators, codes, integrity |
| [Commands](docs/style-guide/ops/commands.md) | `make`, management commands, scripts |

## Stack

- Python 3.12 · Django 5.2 · Django REST Framework · drf-spectacular
- PostgreSQL {{cookiecutter.postgres_version}} · modular `config/settings/` layout
- Production via Docker Compose (self-hosted, not Heroku)
{%- if cookiecutter.reverse_proxy == "nginx" %}
- Nginx reverse proxy (static + media + app)
{%- elif cookiecutter.reverse_proxy == "traefik" %}
- Traefik reverse proxy
{%- endif %}
{%- if cookiecutter.use_jwt == "y" %}
- JWT authentication (`users` app)
{%- else %}
- Session authentication (`users` app)
{%- endif %}
{%- if cookiecutter.use_asgi == "y" %}
- ASGI via Uvicorn
{%- endif %}
{%- if cookiecutter.use_websockets == "y" %}
- Django Channels / WebSockets
{%- endif %}
{%- if cookiecutter.use_redis == "y" %}
- Redis 7.4.9 caching
{%- endif %}
{%- if cookiecutter.use_rabbitmq == "y" %}
- RabbitMQ message broker
{%- endif %}
{%- if cookiecutter.use_celery == "y" %}
- Celery worker + beat (broker: {{cookiecutter.celery_broker}})
{%- endif %}
{%- if cookiecutter.use_code_style == "y" %}
- Ruff linting/formatting · pre-commit hooks
{%- else %}
- flake8 linting
{%- endif %}
{%- if cookiecutter.use_ci == "y" and cookiecutter.ci_provider == "github" %}
- GitHub Actions CI (`.github/workflows/ci.yml`)
{%- elif cookiecutter.use_ci == "y" and cookiecutter.ci_provider == "gitlab" %}
- GitLab CI (`.gitlab-ci.yml`)
{%- endif %}

## Prerequisites

- Python 3.12
- Docker and Docker Compose
- virtualenv (or pyenv)

## Development setup

```bash
cd {{cookiecutter.project_name}}

python3.12 -m venv venv
source venv/bin/activate

pip install -r requirements_dev.txt
{%- if cookiecutter.use_code_style == "y" %}
pre-commit install
{%- endif %}

cp .env.example .env

./start-dev-services.sh
python manage.py devserver
```

Defaults work with local Compose services. `devserver` runs migrations, creates a default superuser (`admin@example.com` / `admin`), and starts the server{%- if cookiecutter.use_celery == "y" %} (plus a Celery worker){%- endif %}.

Use `./start-dev-services.sh --clean` to wipe volumes and start fresh.

More detail: [Commands](docs/style-guide/ops/commands.md) · [Docker & production](docs/style-guide/ops/docker-and-production.md) · [Logging](docs/style-guide/ops/logging.md).

## URLs (local, DEBUG)

| URL | Description |
|-----|-------------|
| http://localhost:8000/ | Swagger UI (**DEBUG only**) |
| http://localhost:8000/redoc/ | ReDoc (**DEBUG only**) |
| http://localhost:8000/schema/ | OpenAPI schema (**DEBUG only**) |
| http://localhost:8000/admin/ | Django admin |
| http://localhost:8000/api/v1/ | API routes (v1) |
| http://localhost:8000/api/v1/health/ | Health check |

Auth, register, and profile endpoints: [Authentication](docs/style-guide/http/authentication.md).

## Creating a domain app

Do **not** use Django’s default `startapp`:

```bash
python manage.py start_domain_app blogs
python manage.py start_domain_app blogs --register
```

Full layout and checklist: [Domain apps](docs/style-guide/overview/domain-apps.md).

## Useful commands

| Command | Description |
|---------|-------------|
| `make install` | Install `requirements_dev.txt` |
| `make up` / `make down` | Start/stop local Docker infra |
| `make test` | Run pytest |
| `make lint` / `make format` | Lint / auto-format |
| `make migrate` | Apply migrations |
| `make runserver` | `manage.py devserver` |
| `python manage.py start_domain_app <name>` | Scaffold a domain app |
| `./scripts/update_translations.sh` | Update `.po` translation files |
| `docker compose up --build -d` | Start production stack |

See [Commands](docs/style-guide/ops/commands.md) for the full reference.

## Production

Self-hosted Compose — configure `.env` (`DJANGO_SETTINGS_MODULE=config.django.production`, strong `SECRET_KEY`, `ALLOWED_HOSTS`, HTTPS flags), then:

```bash
docker compose up --build -d
```

Details: [Docker & production](docs/style-guide/ops/docker-and-production.md).
