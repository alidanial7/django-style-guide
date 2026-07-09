# {{cookiecutter.project_name}}

Django REST API project generated from the [Django Style Guide](https://github.com/alidanial7/django_style_guide) cookiecutter.

Based on the [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide).

## Stack

- Python 3.12 · Django 5.2 · Django REST Framework · drf-spectacular
- PostgreSQL · modular `config/settings/` layout
- Production via Docker Compose (self-hosted, not Heroku)
{%- if cookiecutter.use_jwt == "y" %}
- JWT authentication (`users`, `authentication` apps)
{%- endif %}
{%- if cookiecutter.use_redis == "y" %}
- Redis caching
{%- endif %}
{%- if cookiecutter.use_rabbitmq == "y" %}
- RabbitMQ message broker
{%- endif %}
{%- if cookiecutter.use_celery == "y" %}
- Celery worker + beat
{%- endif %}
{%- if cookiecutter.use_code_style == "y" %}
- Ruff linting/formatting · pre-commit hooks
{%- else %}
- flake8 linting
{%- endif %}

## Prerequisites

- Python 3.12
- Docker and Docker Compose
- virtualenv (or pyenv)

## Development setup

### 1. Enter the project

```bash
cd {{cookiecutter.project_name}}
```

### 2. Create and activate a virtualenv

```bash
python3.12 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements_dev.txt
{%- if cookiecutter.use_code_style == "y" %}
pre-commit install
{%- endif %}
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` if needed. Defaults work with the local Docker Compose services.

### 5. Start development infrastructure

In one terminal:

```bash
./start-dev-services.sh
```

This starts:

| Service | Address |
|---------|---------|
| PostgreSQL | `localhost:5432` |
{%- if cookiecutter.use_redis == "y" %}
| Redis | `localhost:6379` |
{%- endif %}
{%- if cookiecutter.use_rabbitmq == "y" %}
| RabbitMQ | `localhost:5672` |
{%- endif %}
{%- if cookiecutter.use_pgadmin == "y" %}
| pgAdmin | http://localhost:5050 |
{%- endif %}

Use `./start-dev-services.sh --clean` to wipe volumes and start fresh.

### 6. Run the application

Recommended — runs migrations, creates a default superuser, and starts the server{%- if cookiecutter.use_celery == "y" %} (plus a Celery worker in the background){%- endif %}:

```bash
python manage.py devserver
```

Or run Django only:

```bash
python manage.py migrate
python manage.py runserver
```

### Default superuser

Created automatically by `devserver` if it does not exist:

{%- if cookiecutter.use_jwt == "y" %}
- Email: `admin@example.com`
- Password: `admin`
{%- else %}
- Username: `admin`
- Password: `admin`
{%- endif %}

## URLs

| URL | Description |
|-----|-------------|
| http://localhost:8000/ | Swagger UI |
| http://localhost:8000/redoc/ | ReDoc |
| http://localhost:8000/schema/ | OpenAPI schema |
| http://localhost:8000/admin/ | Django admin |
| http://localhost:8000/api/ | API routes |

## Project structure

```
{{cookiecutter.project_name}}/
├── config/
│   ├── django/           # base, local, production, test
│   ├── settings/         # modular settings slices
│   ├── urls.py
│   ├── celery.py         # Celery app factory
│   └── tasks.py
├── {{cookiecutter.project_slug}}/
│   ├── api/              # DRF urls, handlers, pagination
│   ├── core/
│   ├── common/
│   ├── commands/         # management commands (devserver)
{%- if cookiecutter.use_jwt == "y" %}
│   ├── users/
│   └── authentication/
{%- endif %}
├── docker/               # Dockerfiles and entrypoints
├── docker-compose.yml    # production
├── docker-compose.dev.yml
├── start-dev-services.sh
├── scripts/
│   └── update_translations.sh
└── locale/               # created by makemessages
```

Settings are composed in `config/django/base.py` from `config/settings/*.py` modules.

## Translations

Update translation files:

```bash
./scripts/update_translations.sh
./scripts/update_translations.sh --compile-messages
```

## Testing

```bash
pytest
```

Uses `config.django.test` (SQLite, eager Celery{%- if cookiecutter.use_celery == "y" %}{%- else %}, no Celery{%- endif %}).

## Code quality

{%- if cookiecutter.use_code_style == "y" %}
```bash
ruff check .
ruff format .
pre-commit run --all-files
```
{%- else %}
```bash
flake8
mypy .
```
{%- endif %}

## Production (Docker Compose)

Self-hosted production — no Heroku or third-party PaaS.

### 1. Configure environment

```bash
cp .env.example .env
```

Set `DJANGO_SETTINGS_MODULE=config.django.production`, a strong `SECRET_KEY`, and `ALLOWED_HOSTS`.

{%- if cookiecutter.use_sentry == "y" %}
Optionally set `SENTRY_DSN` to enable Sentry (only activates when the DSN is set).
{%- endif %}

### 2. Build and start

```bash
docker compose up --build -d
```

This starts:

- PostgreSQL
{%- if cookiecutter.use_rabbitmq == "y" %}
- RabbitMQ
{%- endif %}
- Django (gunicorn on port 8000)
{%- if cookiecutter.use_celery == "y" %}
- Celery worker
- Celery beat
{%- endif %}

App: http://localhost:8000

## Useful commands

| Command | Description |
|---------|-------------|
| `./start-dev-services.sh` | Start dev Docker services |
| `python manage.py devserver` | Migrate, superuser, runserver{%- if cookiecutter.use_celery == "y" %}, Celery{%- endif %} |
| `python manage.py runserver` | Django dev server only |
| `./scripts/update_translations.sh` | Update `.po` translation files |
| `docker compose up --build -d` | Start production stack |
