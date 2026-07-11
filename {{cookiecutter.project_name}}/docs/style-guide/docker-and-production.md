# 🐳 Docker & production

> Local infrastructure vs production Compose, reverse proxies, env hardening, and CI.
>
> Production is **self-hosted Docker Compose** — not Heroku or a proprietary PaaS.

---

## 🎯 Two Compose files

```mermaid
flowchart TB
    subgraph Dev["Local development"]
        DEV[docker-compose.dev.yml]
        APP[Django on host via venv]
        DEV -->|Postgres{% if cookiecutter.use_redis == "y" %} / Redis{% endif %}{% if cookiecutter.use_rabbitmq == "y" %} / RabbitMQ{% endif %}{% if cookiecutter.use_pgadmin == "y" %} / pgAdmin{% endif %}| APP
    end
    subgraph Prod["Production-like"]
        PROD[docker-compose.yml]
        PROD --> DJ[django container]
        PROD --> DB[(postgres)]
{%- if cookiecutter.use_celery == "y" %}
        PROD --> CW[celery worker + beat]
{%- endif %}
{%- if cookiecutter.reverse_proxy != "none" %}
        PROD --> RP[reverse proxy]
{%- endif %}
    end
```

| File | Role |
|------|------|
| `docker-compose.dev.yml` + `./start-dev-services.sh` | Only dependencies; **app runs on the host** |
| `docker-compose.yml` + `docker/` | Full stack image(s) with `config.django.production` |

---

## 💻 Local infrastructure

```bash
./start-dev-services.sh
./start-dev-services.sh --clean   # wipe volumes, fresh DB
make up                           # same as start-dev-services.sh
make down                         # stop dev compose
```

Typical published ports (defaults):

| Service | Address |
|---------|---------|
| PostgreSQL {{cookiecutter.postgres_version}} | `localhost:5432` |
{%- if cookiecutter.use_redis == "y" %}
| Redis 7.4.9 | `localhost:6379` |
{%- endif %}
{%- if cookiecutter.use_rabbitmq == "y" %}
| RabbitMQ | `localhost:5672` |
{%- endif %}
{%- if cookiecutter.use_pgadmin == "y" %}
| pgAdmin | http://localhost:5050 |
{%- endif %}

Then on the host:

```bash
cp .env.example .env
python manage.py devserver
# or: make runserver
```

`devserver` migrates, ensures a default superuser, and starts the app{%- if cookiecutter.use_celery == "y" %} (plus a Celery worker in the background){%- endif %}. Details: [Commands](commands.md).

Health for local/prod app: `GET /api/v1/health/` — status + latency only, no secrets.

---

## 🏭 Production Compose

```bash
cp .env.example .env
# set DJANGO_SETTINGS_MODULE=config.django.production
# set strong SECRET_KEY, ALLOWED_HOSTS, …

docker compose up --build -d
```

### What starts

| Service | Notes |
|---------|-------|
| PostgreSQL | Internal network; not published by default |
{%- if cookiecutter.use_redis == "y" %}
| Redis | Cache{%- if cookiecutter.use_celery == "y" and cookiecutter.celery_broker == "redis" %} / Celery broker{% endif %} |
{%- endif %}
{%- if cookiecutter.use_rabbitmq == "y" %}
| RabbitMQ | Broker / messaging |
{%- endif %}
| Django | Image from `docker/production.Dockerfile`; entrypoint `docker/web_entrypoint.sh` |
{%- if cookiecutter.use_asgi == "y" %}
| | ASGI via Uvicorn on port 8000 |
{%- else %}
| | Gunicorn on port 8000 |
{%- endif %}
{%- if cookiecutter.use_celery == "y" %}
| Celery worker + beat | Same image, different command |
{%- endif %}
{%- if cookiecutter.reverse_proxy == "nginx" %}
| Nginx | Port 80; proxies app; serves `/static/` and `/media/` |
{%- elif cookiecutter.reverse_proxy == "traefik" %}
| Traefik | Port 80; proxies app; configure TLS for real domains |
{%- endif %}

{%- if cookiecutter.reverse_proxy == "none" %}
App URL: http://localhost:8000 — Django may serve media from the volume. Prefer regenerating with `reverse_proxy=nginx` (or traefik) for real traffic.
{%- elif cookiecutter.reverse_proxy == "nginx" %}
App URL: http://localhost/
{%- else %}
App URL: http://localhost/
{%- endif %}

Production Compose **does not bind-mount source**. Rebuild after code changes:

```bash
docker compose up --build -d
```

Volumes typically persist Postgres data, media, and collected static files.

---

## 🔐 Environment hardening

Before exposing the stack:

| Variable / flag | Purpose |
|-----------------|---------|
| `SECRET_KEY` | Strong unique secret |
| `ALLOWED_HOSTS` | Your domain(s) |
| `DJANGO_SETTINGS_MODULE=config.django.production` | Production settings entrypoint |
| `SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE` | HTTPS-only cookies |
| `SECURE_SSL_REDIRECT` / `SECURE_HSTS_SECONDS` | Force HTTPS + HSTS |
| `CSRF_TRUSTED_ORIGINS` | `https://your.domain` |
{%- if cookiecutter.use_sentry == "y" %}
| `SENTRY_DSN` | Optional; Sentry activates only when set |
{%- endif %}

Never commit a filled `.env`. Use secrets management / host env in real deployments.

Swagger / schema routes are **DEBUG-only** — they stay off under production settings. See [Swagger](swagger.md).

---

## 📁 Docker-related paths

| Path | Role |
|------|------|
| `docker/production.Dockerfile` | App image |
| `docker/web_entrypoint.sh` | Migrate / collectstatic / start server (as shipped) |
| `docker/nginx/` or `docker/traefik/` | Proxy configs when selected |
| `docker-compose.yml` | Production stack |
| `docker-compose.dev.yml` | Dev dependencies only |

---

{%- if cookiecutter.use_ci == "y" %}
## 🔄 Continuous integration

{%- if cookiecutter.ci_provider == "github" %}
Workflow: `.github/workflows/ci.yml` at the project root.

Runs on pushes/PRs to `main`/`master`: lint, mypy, `manage.py check`{%- if cookiecutter.use_testing == "y" %}, and `pytest` with coverage against a Postgres service{%- endif %}.
{%- elif cookiecutter.ci_provider == "gitlab" %}
Config: `.gitlab-ci.yml`.

Pipeline stage `check`: lint, mypy, `manage.py check`{%- if cookiecutter.use_testing == "y" %}, and `pytest` (Postgres service){%- endif %}.
{%- endif %}

CI uses{%- if cookiecutter.use_testing == "y" %} `config.django.test` with Postgres{%- else %} `config.django.local`-style checks with a SQLite `DATABASE_URL` where applicable{%- endif %}. See [Testing](testing.md) and [Code quality](code-quality.md).
{%- else %}
## Continuous integration

CI was not enabled at generation (`use_ci=n`). Add GitHub Actions or GitLab CI later using the same lint/test commands as `Makefile`.
{%- endif %}

---

## 🩺 Operations tips

| Tip | Detail |
|-----|--------|
| Health checks | Compose waits on Postgres{%- if cookiecutter.use_redis == "y" %} / Redis{% endif %} health before starting Django |
| Logs | JSON files under `logs/` when `LOG_TO_FILE=true`; prefer shipping container stdout to your log stack — see [Logging](logging.md) |
| Throttles | Use Redis-backed cache in multi-worker prod — see [Throttling](throttling.md) |
| Migrations | Run via entrypoint or explicit `manage.py migrate` in the django service |
| Static/media | Prefer reverse proxy serving volumes in production |

---

## ❌ Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| Running `config.django.local` in the public internet | Use `production` + HTTPS flags |
| Publishing Postgres to `0.0.0.0` without need | Keep DB on the internal Compose network |
| Bind-mounting code into prod Compose and “hot reload” | Rebuild images for deploys |
| Leaving `DEBUG=True` / default `SECRET_KEY` | Fail closed |
| Expecting Swagger at `/` in production | DEBUG-only by design |

---

## ✅ Deploy checklist

1. Strong secrets + `ALLOWED_HOSTS` + HTTPS cookie flags  
2. `docker compose up --build -d`  
3. Hit `/api/v1/health/`  
4. Confirm reverse proxy serves static/media (if enabled)  
5. Confirm migrations applied  
6. Confirm logs/monitoring destination  

---

## 🔗 Related docs

| Doc | Why |
|-----|-----|
| [Commands](commands.md) | `make`, `devserver`, scripts |
| [Settings](settings.md) | `production` vs `local` |
| [Logging](logging.md) | File / console logs |
| [Throttling](throttling.md) | Redis for shared limits |
| [Project structure](project-structure.md) | Where `docker/` lives |
