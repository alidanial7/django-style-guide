<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/django/django-plain.svg" width="72" alt="Django" />
</p>

<h1 align="center">Django Style Guide</h1>

<p align="center">
  <strong>Ship a production-ready Django REST API in minutes</strong><br/>
  HackSoft layers · Docker Compose · OpenAPI · Cursor-ready agent rules
</p>

<p align="center">
  <a href="VERSION"><img src="https://img.shields.io/badge/template-1.3.0-0B5FFF?style=for-the-badge" alt="Version" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" /></a>
  <a href="https://www.djangoproject.com/"><img src="https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-2ea44f?style=for-the-badge" alt="License" /></a>
</p>

<p align="center">
  <a href="https://www.django-rest-framework.org/"><img src="https://img.shields.io/badge/DRF-API-a30000?style=flat-square&logo=django&logoColor=white" alt="DRF" /></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker" /></a>
  <a href="https://github.com/HackSoftware/Django-Styleguide"><img src="https://img.shields.io/badge/HackSoft-Styleguide-111827?style=flat-square" alt="HackSoft" /></a>
  <a href="https://github.com/cookiecutter/cookiecutter"><img src="https://img.shields.io/badge/Cookiecutter-ready-D4AA00?style=flat-square&logo=cookiecutter&logoColor=white" alt="Cookiecutter" /></a>
  <a href="https://cursor.com/"><img src="https://img.shields.io/badge/Cursor-agent%20rules-000000?style=flat-square" alt="Cursor" /></a>
</p>

---

A [Cookiecutter](https://github.com/cookiecutter/cookiecutter) template for Django APIs, inspired by the [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide).

You flip switches (JWT, Celery, WebSockets, Unfold admin, file manager…). **Unused code is pruned** — what you generate is what you run.

> 🖥️ Self-hosted with **Docker Compose** on your own server — not a Heroku / PaaS template.

---

## ✨ Why this template

| | | |
|:---:|:---|:---|
| 🏗️ | **Opinionated architecture** | Services / selectors / TypedDicts / HTTP envelope — not a flat “apps + serializers” dump |
| 🎛️ | **Toggle features, lean tree** | Celery, Channels, CI, admin theme, uploads… enabled options stay; the rest is deleted |
| 🤖 | **Agent-ready out of the box** | Slim `AGENTS.md` + glob-scoped `.cursor/rules/` matched to what you enabled |
| 📚 | **Docs that match the code** | Generated `docs/style-guide/` explains *this* project’s conventions |
| ⚡ | **One command to develop** | `manage.py devserver` — migrate, superuser, runserver (optional Celery) |

---

## 🚀 Quick start

### ① Install Cookiecutter *(once)*

```bash
pip install "cookiecutter>=2.4"
```

### ② Generate a project

```bash
cookiecutter https://github.com/alidanial7/django-style-guide.git
```

On a TTY you get a checklist UI (`↑` `↓` or `j` `k` · `Space` · `Enter`).  
Defaults are sensible: **JWT** · **UUID PKs** · **pytest** · **Ruff**.

<details>
<summary>📦 Prefer a local clone?</summary>

```bash
git clone https://github.com/alidanial7/django-style-guide.git
cd django-style-guide
./init.sh
```

</details>

<details>
<summary>📁 Generate into an existing git repo (inplace)</summary>

The wizard asks: **Generate into the current directory?**  
Or force it:

```bash
./init.sh --inplace
# or
DSG_INPLACE=1 ./init.sh
```

**Safety:** the target must be empty **or** only git metadata  
(`.git`, `.gitignore`, `.gitattributes`, `.gitmodules`).

If the directory has other files, the wizard asks **Force-delete those files and generate here?**  
Or skip the prompt:

```bash
./init.sh --inplace-force
# or
DSG_INPLACE_FORCE=1 ./init.sh
```

Force-clean keeps only git metadata, then generates.

**Template-repo safety:** `--inplace-force` **refuses** when cwd is this cookiecutter
template. To intentionally replace the template with a generated app:

```bash
./init.sh --inplace-force-template
# or
DSG_INPLACE_FORCE_TEMPLATE=1 ./init.sh
```

That path snapshots the template aside, force-cleans cwd, then generates (destructive).

`project_name` is still used as a temporary folder name during generation, then contents are moved up into `.`.

</details>

<details>
<summary>🤖 Non-interactive / CI preset</summary>

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

### ③ Run it

```bash
cd MyProject                         # = your project_name
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements_dev.txt
cp .env.example .env
./start-dev-services.sh              # Postgres (+ Redis / … if selected)
python manage.py devserver
```

📖 Open API docs at `/api/docs/` when `DEBUG=True` (Swagger via drf-spectacular; scoped UIs at `/api/docs/<scope>/`).  
Full setup notes live in the **generated** project’s `README.md`.

> 💡 After the interactive UI finishes, the process may exit with code **143**. That is expected — Cookiecutter is stopped so you are not prompted twice.

---

## 📦 What you get

```text
MyProject/
├── ⚙️  config/                 # modular settings (thin base.py aggregator)
├── 🐍  <project_slug>/
│   ├── api/                    # URL router only
│   ├── users/                  # reference domain (auth + profile)
│   ├── common/                 # envelope, BaseModel, integrity helpers
│   ├── commands/               # start_domain_app, devserver, …
│   └── …                       # optional: file_manager, administration, …
├── 📚  docs/style-guide/       # living conventions for this project
├── 🤖  AGENTS.md               # agent index
├── 📐  .cursor/rules/          # glob-scoped rules (feature-gated)
├── 🐳  docker-compose*.yml
└── …
```

### ✅ Always included

- 🔌 Django REST Framework + OpenAPI *(Swagger only when `DEBUG=True`)*
- 🧩 Modular `config/settings/`
- 🐳 Docker Compose for local infra and production
- 👤 `users` app (JWT **or** session)
- 🛠️ `start_domain_app` — HackSoft-style domain scaffolding

### 🎛️ Optional flags

| | Area | Options |
|:---:|:---|:---|
| 🔐 | **Auth & models** | JWT / session · email or username · OTP · Google/Microsoft/Apple · UUID PKs · portal stubs |
| 🗂️ | **Domains** | Multi-scope `/api/v1/<scope>/…` · `ManagedFile` uploads · Unfold admin |
| ⏳ | **Async & cache** | Redis · RabbitMQ · Celery · ASGI · Channels |
| 🚢 | **Ops** | Nginx / Traefik · Sentry · pgAdmin · GitHub or GitLab CI |
| ✨ | **Quality** | Ruff + pre-commit · pytest · VS Code settings |

---

## ⚙️ Configuration options

Defaults match the interactive UI.

### 🏷️ Project

| Option | Default | Description |
|--------|---------|-------------|
| `project_name` | MyProject | Human-readable name (output directory) |
| `project_slug` | auto | Python package (`spaces` / `-` / `.` → `_`) |
| `first_name` / `last_name` | author / … | LICENSE metadata |
| `license` | MIT | `MIT` · `BEER` · `None` |
| `postgres_user` / `postgres_password` | user / password | Local Postgres |
| `postgres_version` | 17.10 | Docker image tag (`17.10` … `14.17`) |

### 🧩 Features

| | Option | Default | Description |
|:---:|--------|---------|-------------|
| 🔑 | `use_jwt` | y | `y` → JWT · `n` → session |
| 👤 | `user_login_field` | email | `email` or `username` (`USERNAME_FIELD`) |
| 📲 | `use_otp_login` | n | Phone OTP (`otp/request` · `otp/verify`) + SMS provider stub · `OTP_TEST` |
| 🔵 | `use_google_login` | n | Google `id_token` → JWT/session |
| 🪟 | `use_microsoft_login` | n | Microsoft `id_token` → JWT/session |
| | `use_apple_login` | n | Apple `id_token` → JWT/session |
| 🌍 | `use_i18n` | n | Django gettext (`LocaleMiddleware`, `locale/`, `update_translations`) |
| | `i18n_mode` | bilingual | `monolingual` (en) or `bilingual` (en+fa); ignored when `use_i18n=n` |
| 🆔 | `use_uuid_pk` | y | UUID PK on `BaseModel` |
| 🌐 | `use_scoped_apis` | n | Multi-scope `/api/v1/<scope>/` + `/api/docs/<scope>/` |
| | `api_scopes` | `admin,factory` | Comma-separated lowercase names (e.g. `admin,factory,customer`); ignored if scoped APIs are off |
| 📁 | `use_file_manager` | n | `ManagedFile` uploads app |
| 🎨 | `use_unfold_admin` | n | Django Unfold + `administration/` |
| 🛂 | `use_portal_permissions` | n | `IsAdmin` / `IsCustomer` stubs |
| 🏗️ | `infra_repo_name` | _(empty)_ | Named infra repo in deploy-alert text |
| 🛰️ | `use_sentry` | n | Sentry when `SENTRY_DSN` is set |
| 💻 | `use_vscode` | n | VS Code settings |
| 🗄️ | `use_pgadmin` | n | pgAdmin in dev Compose (`:5050`) |
| 🔴 | `use_redis` | n | Redis cache (+ OTP / Celery Redis / WebSockets) |
| 🐇 | `use_rabbitmq` | n | RabbitMQ broker |
| 🥬 | `use_celery` | n | Worker + beat |
| 🔗 | `celery_broker` | redis | `redis` or `rabbitmq` |
| 🦄 | `use_asgi` | n | Uvicorn instead of Gunicorn |
| 📡 | `use_websockets` | n | Django Channels (needs ASGI + Redis) |
| 🔀 | `reverse_proxy` | none | `none` · `nginx` · `traefik` |
| 🧹 | `use_code_style` | y | Ruff + pre-commit |
| 🪝 | `precommit_*` | y | Hygiene / pyupgrade / Ruff / pydoclint / i18n lint |
| 🧪 | `use_testing` | y | pytest + default tests |
| 🤖 | `use_ci` | n | CI pipeline |
| 🐙 | `ci_provider` | github | `github` or `gitlab` |

### 🔗 Option dependencies

| Rule | Requirement |
|------|-------------|
| 🌐 Multi-scope | `use_scoped_apis=y` needs non-empty `api_scopes` (e.g. `admin,factory`) |
| 📲 OTP | `use_redis=y` (shared challenges across workers; UI / pre_gen enforce) |
| 🥬 Celery → broker | Redis broker → `use_redis=y` · RabbitMQ broker → `use_rabbitmq=y` |
| 📡 WebSockets | `use_asgi=y` **and** `use_redis=y` |
| 🤖 CI | Pick `ci_provider` when `use_ci=y` |
| 🧹 Code style | Enable at least one `precommit_*=y` (UI turns all on if empty) |

---

## 🧭 After generation

| | Audience | Start here |
|:---:|:---|:---|
| 👤 | Day-to-day setup | Generated project `README.md` |
| 📖 | Architecture & conventions | [`docs/style-guide/`]({{cookiecutter.project_name}}/docs/style-guide/README.md) |
| 🤖 | Coding agents | Generated `AGENTS.md` + `.cursor/rules/` |

Template source for the style guide: [`{{cookiecutter.project_name}}/docs/style-guide/`]({{cookiecutter.project_name}}/docs/style-guide/).

---

## 🛠️ Template contributors

Working on **this** repo (not a generated app):

```bash
make choices   # cookiecutter.json ↔ interactive UI maps
make smoke     # option matrices + agent-surface asserts → _gen_smoke/
```

See [`AGENTS.md`](AGENTS.md) and `.cursor/rules/` for hooks, prompts, and prune logic.

---

## 🤝 Contributing

Issues and PRs welcome → [github.com/alidanial7/django-style-guide](https://github.com/alidanial7/django-style-guide)

## 📄 License

MIT
