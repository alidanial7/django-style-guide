# Django Style Guide

**Ship a production-ready Django REST API in minutes** — HackSoft layers, Docker Compose, OpenAPI, and Cursor-ready agent rules baked in.

[![Version](https://img.shields.io/badge/template-1.2.0-0B5FFF?style=flat-square)](VERSION)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

A [Cookiecutter](https://github.com/cookiecutter/cookiecutter) template for Django APIs, inspired by the [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide).  
You pick the pieces (JWT, Celery, WebSockets, Unfold admin, file manager…). Unused code is pruned — what you generate is what you run.

> Self-hosted with **Docker Compose** on your own server. Not a Heroku / PaaS template.

---

## Why this template

| | |
|---|---|
| **Opinionated architecture** | Services / selectors / TypedDicts / HTTP envelope — not a flat “apps + serializers” dump |
| **Toggle features, keep the tree lean** | Celery, Channels, CI, admin theme, uploads… enabled options stay; the rest is deleted |
| **Agent-ready out of the box** | Slim `AGENTS.md` + glob-scoped `.cursor/rules/` matched to what you enabled |
| **Docs that match the code** | Generated `docs/style-guide/` explains *this* project’s conventions, not a generic tutorial |
| **One command to develop** | `manage.py devserver` — migrate, superuser, runserver (optional Celery) |

---

## Quick start

**1. Install Cookiecutter** (once)

```bash
pip install "cookiecutter>=2.4"
```

**2. Generate a project**

```bash
cookiecutter https://github.com/alidanial7/django-style-guide.git
```

On a TTY you get a checklist UI (↑/↓, Space, Enter). Defaults are sensible: JWT, UUID PKs, pytest, Ruff.

<details>
<summary>Prefer a local clone?</summary>

```bash
git clone https://github.com/alidanial7/django-style-guide.git
cd django-style-guide
./init.sh
```

</details>

<details>
<summary>Non-interactive / CI preset</summary>

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

With `--no-input`, set Celery / WebSockets / CI dependencies yourself or `pre_gen` will reject the combo.

</details>

**3. Run it**

```bash
cd MyProject                         # = your project_name
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements_dev.txt
cp .env.example .env
./start-dev-services.sh              # Postgres (+ Redis / … if selected)
python manage.py devserver
```

Open the API docs when `DEBUG=True` (Swagger via drf-spectacular). Full setup notes live in the **generated** project’s `README.md`.

> **Note:** After the interactive UI finishes, the process may exit with code **143**. That is expected — Cookiecutter is stopped so you are not prompted twice.

---

## What you get

```text
MyProject/
├── config/                 # modular settings (thin base.py aggregator)
├── <project_slug>/
│   ├── api/                # URL router only
│   ├── users/              # reference domain (auth + profile)
│   ├── common/             # envelope, BaseModel, integrity helpers
│   ├── commands/           # start_domain_app, devserver, …
│   └── …                   # optional: file_manager, administration, …
├── docs/style-guide/       # living conventions for this project
├── AGENTS.md               # agent index
├── .cursor/rules/          # glob-scoped rules (feature-gated)
├── docker-compose*.yml
└── …
```

**Always on**

- Django REST Framework + OpenAPI (Swagger only when `DEBUG=True`)
- Modular `config/settings/`
- Docker Compose for local infra and production
- `users` app (JWT **or** session)
- `start_domain_app` — HackSoft-style domain scaffolding

**Optional (flags)**

| Area | Options |
|------|---------|
| Auth & models | JWT / session · UUID / BigAutoField PKs · portal permission stubs |
| Domains | Scoped `/api/v1/site/…` sample · `ManagedFile` uploads · Unfold admin |
| Async & cache | Redis · RabbitMQ · Celery (Redis or Rabbit broker) · ASGI · Channels |
| Ops | Nginx / Traefik · Sentry · pgAdmin · GitHub or GitLab CI |
| Quality | Ruff + pre-commit · pytest suite · VS Code settings |

---

## Configuration options

Grouped for scanning. Defaults match the interactive UI.

### Project

| Option | Default | Description |
|--------|---------|-------------|
| `project_name` | MyProject | Human-readable name (output directory) |
| `project_slug` | auto | Python package (`spaces` / `-` / `.` → `_`) |
| `first_name` / `last_name` | author / … | LICENSE metadata |
| `license` | MIT | `MIT`, `BEER`, or `None` |
| `postgres_user` / `postgres_password` | user / password | Local Postgres |
| `postgres_version` | 17.10 | Docker image tag (`17.10` … `14.17`) |

### Features

| Option | Default | Description |
|--------|---------|-------------|
| `use_jwt` | y | `y` → JWT · `n` → session |
| `use_uuid_pk` | y | UUID PK on `BaseModel` |
| `use_scoped_apis` | n | Sample site mount + per-client schema helper |
| `use_file_manager` | n | `ManagedFile` uploads app |
| `use_unfold_admin` | n | Django Unfold + `administration/` |
| `use_portal_permissions` | n | `IsAdmin` / `IsCustomer` stubs |
| `infra_repo_name` | _(empty)_ | Named infra repo in deploy-alert text |
| `use_sentry` | n | Sentry when `SENTRY_DSN` is set |
| `use_vscode` | n | VS Code settings |
| `use_pgadmin` | n | pgAdmin in dev Compose (`:5050`) |
| `use_redis` | n | Redis cache (+ Celery Redis / WebSockets) |
| `use_rabbitmq` | n | RabbitMQ broker |
| `use_celery` | n | Worker + beat |
| `celery_broker` | redis | `redis` or `rabbitmq` |
| `use_asgi` | n | Uvicorn instead of Gunicorn |
| `use_websockets` | n | Django Channels (needs ASGI + Redis) |
| `reverse_proxy` | none | `none` · `nginx` · `traefik` |
| `use_code_style` | y | Ruff + pre-commit |
| `precommit_*` | y | Hygiene / pyupgrade / Ruff / pydoclint / translation lint |
| `use_testing` | y | pytest + default tests |
| `use_ci` | n | CI pipeline |
| `ci_provider` | github | `github` or `gitlab` |

### Option dependencies

- **Celery → broker**: Redis broker needs `use_redis=y`; RabbitMQ broker needs `use_rabbitmq=y`
- **WebSockets →** `use_asgi=y` **and** `use_redis=y`
- **CI →** pick `ci_provider` when `use_ci=y`
- **Code style →** enable at least one `precommit_*=y` (UI turns all on if you leave them empty)

---

## After generation

| Audience | Start here |
|----------|------------|
| Day-to-day setup | Generated project `README.md` |
| Architecture & conventions | [`docs/style-guide/`]({{cookiecutter.project_name}}/docs/style-guide/README.md) |
| Coding agents | Generated `AGENTS.md` + `.cursor/rules/` |

Template source for the style guide lives under [`{{cookiecutter.project_name}}/docs/style-guide/`]({{cookiecutter.project_name}}/docs/style-guide/).

---

## Template contributors

Working on **this** repo (not a generated app):

```bash
make choices   # cookiecutter.json ↔ interactive UI maps
make smoke     # option matrices + agent-surface asserts → _gen_smoke/
```

See [`AGENTS.md`](AGENTS.md) and `.cursor/rules/` for how hooks, prompts, and prune logic fit together.

---

## Contributing

Issues and PRs welcome → [github.com/alidanial7/django-style-guide](https://github.com/alidanial7/django-style-guide)

## License

MIT
