# 🛠️ Commands

> Day-to-day entrypoints: `Makefile`, management commands, and project scripts.
>
> Prefer these wrappers so locals and CI share the same verbs (`make test`, `make lint`, …).

---

## 🎯 Quick map

| You want to… | Command |
|--------------|---------|
| Install deps | `make install` |
| Start local DB{/Redis/…} | `make up` or `./start-dev-services.sh` |
| Stop local infra | `make down` |
| Run app (migrate + superuser + server) | `make runserver` or `python manage.py devserver` |
| Migrate | `make migrate` |
| Tests | `make test` |
| Lint / format | `make lint` / `make format` |
| Django check | `make check` |
| Shell | `make shell` |
| New domain app | `python manage.py start_domain_app <name>` |
| Translations | `./scripts/update_translations.sh` |
| Production stack | `docker compose up --build -d` |

---

## 📦 Makefile targets

Defined in the project root `Makefile`:

| Target | Action |
|--------|--------|
| `make install` | `pip install -r requirements_dev.txt`{%- if cookiecutter.use_code_style == "y" %} + `pre-commit install`{% endif %} |
| `make up` | `./start-dev-services.sh` |
| `make down` | `docker compose -f docker-compose.dev.yml down` |
| `make migrate` | `manage.py migrate` |
| `make makemigrations` | `manage.py makemigrations` |
| `make runserver` | `manage.py devserver` |
| `make check` | `manage.py check` |
| `make shell` | `shell_plus` if available, else `shell` |
{%- if cookiecutter.use_testing == "y" %}
| `make test` | `pytest -q` |
{%- else %}
| `make test` | Exits with a message that testing was not enabled |
{%- endif %}
{%- if cookiecutter.use_code_style == "y" %}
| `make lint` | `ruff check` + `ruff format --check` |
| `make format` | `ruff check --fix` + `ruff format` |
{%- else %}
| `make lint` | `flake8` |
| `make format` | Not enabled (`use_code_style=n`) |
{%- endif %}

Override interpreter if needed: `make test PYTHON=python3.12`.

---

## 🧩 Management commands

### `devserver`

```bash
python manage.py devserver
```

Typical behavior (template):

1. Apply migrations  
2. Ensure default superuser exists (`admin@example.com` / `admin` — **local only**)  
3. Start the development server  
{%- if cookiecutter.use_celery == "y" %}
4. Start a Celery worker in the background when Celery is enabled  
{%- endif %}

For Django-only without the extras:

```bash
python manage.py migrate
python manage.py runserver
```

### `start_domain_app`

```bash
python manage.py start_domain_app blogs
python manage.py start_domain_app blogs --register
python manage.py start_domain_app blogs --force
python manage.py start_domain_app blogs --no-tests
```

Scaffolds the style-guide layout (models/services/selector/apis/…). Full guide: [Domain apps](../structure/domain-apps.md).

---

## 📜 Scripts

| Script | Purpose |
|--------|---------|
| `./start-dev-services.sh` | Start (or `--clean` recreate) `docker-compose.dev.yml` services |
| `./scripts/update_translations.sh` | `makemessages` workflow; `--compile-messages` optional — see [Translations](translations.md) |

---

## 🌐 Useful URLs (local DEBUG)

| URL | Description |
|-----|-------------|
| http://localhost:8000/ | Swagger UI (**DEBUG only**) |
| http://localhost:8000/redoc/ | ReDoc (**DEBUG only**) |
| http://localhost:8000/schema/ | OpenAPI schema (**DEBUG only**) |
| http://localhost:8000/admin/ | Django admin |
| http://localhost:8000/api/v1/ | API v1 |
| http://localhost:8000/api/v1/health/ | Health check |

Auth/register paths: [Authentication](../http/authentication.md), [URLs](../layers/urls.md).

### Default superuser (`devserver`)

| Field | Value |
|-------|-------|
| Email | `admin@example.com` |
| Password | `admin` |

Change immediately outside throwaway local environments.

---

## 🐳 Production commands

```bash
docker compose up --build -d
docker compose logs -f django
docker compose exec django python manage.py migrate
docker compose down
```

See [Docker & production](docker-and-production.md).

---

## ❌ Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| Committing with secrets in shell history demos | Use `.env`, never paste prod keys into docs/commands |
| Using `startapp` instead of `start_domain_app` | Style-guide layout |
| Running production Compose with `.env` defaults | Harden secrets first |
| Skipping `make lint` / hooks before PR | [Code quality](code-quality.md) |

---

## ✅ Daily loop

```bash
make up
make migrate          # if needed
make runserver
# … code …
make lint
make test
```

---

## 🔗 Related docs

| Doc | Why |
|-----|-----|
| [Docker & production](docker-and-production.md) | Compose details |
| [Domain apps](../structure/domain-apps.md) | `start_domain_app` |
| [Code quality](code-quality.md) | Lint/format |
| [Testing](testing.md) | pytest |
| [Translations](translations.md) | i18n script |
