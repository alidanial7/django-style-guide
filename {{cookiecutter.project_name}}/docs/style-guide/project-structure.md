# Project structure

```text
{{cookiecutter.project_name}}/
├── config/
│   ├── django/              # base, local, production, test entrypoints
│   ├── settings/            # modular settings slices
│   ├── logging_formatters.py
│   ├── request_id.py        # X-Request-ID middleware + log filter
│   ├── urls.py              # admin, /api/v1/, DEBUG Swagger
│   ├── celery.py            # Celery app factory (if enabled)
│   ├── tasks.py
│   ├── asgi.py / wsgi.py
│   └── env.py               # env helpers
├── {{cookiecutter.project_slug}}/
│   ├── api/                 # versioned URL include, mixins, pagination
│   ├── core/                # health, ApplicationError, routing hooks
│   ├── common/              # platform: http, errors, validators, db/integrity, services
│   ├── commands/            # management commands
│   ├── users/               # identity domain app
│   ├── utils/               # thin shared helpers / test bases
│   └── conftest.py          # pytest fixtures (if testing enabled)
├── docker/                  # Dockerfiles, nginx/traefik configs
├── docs/
│   └── style-guide/         # this documentation
├── logs/                    # runtime logs (gitignored content; .gitkeep kept)
├── scripts/                 # e.g. update_translations.sh
├── requirements/            # base, local, production splits
├── docker-compose.yml       # production
├── docker-compose.dev.yml   # local infrastructure
├── start-dev-services.sh
├── manage.py
└── Makefile
```

## `config/`

Settings are **not** one giant `settings.py`. `config/django/base.py` imports slices from `config/settings/*.py`:

| Module | Typical contents |
|--------|------------------|
| `apps.py` | `LOCAL_APPS`, `THIRD_PARTY_APPS`, `INSTALLED_APPS` |
| `auth.py` | `AUTH_USER_MODEL`, `AUTH_PASSWORD_VALIDATORS` |
| `database.py` | DB from `DATABASE_URL` |
| `drf.py` | REST framework defaults, exception handler, throttle rates |
| `swagger.py` | `SPECTACULAR_SETTINGS` |
| `logging.py` | Logging dict config |
| `jwt.py` | SimpleJWT (when JWT selected) |
| `security.py` / `cors.py` / `sessions.py` | Hardening and cookies |
| `celery.py` / `channels.py` / `sentry.py` | Optional stacks |

Environment entrypoints:

| Module | Use |
|--------|-----|
| `config.django.local` | Development |
| `config.django.production` | Production Compose |
| `config.django.test` | pytest / CI |

## Package apps (`{{cookiecutter.project_slug}}/`)

Local apps are registered in `config/settings/apps.py` via full `AppConfig` paths, e.g.:

```python
"{{cookiecutter.project_slug}}.users.apps.UsersConfig"
```

Reserved package names (do not scaffold as domain apps): `api`, `common`, `commands`, `config`, `core`, and similar — see `start_domain_app`.

## Docs layout

| Path | Purpose |
|------|---------|
| `README.md` (project root) | Quick start and stack overview |
| `docs/README.md` | Docs index |
| `docs/style-guide/` | Coding conventions and reference |

See [Domain apps](domain-apps.md) for the per-app folder layout.
