import os

from config.env import env

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="psql://{{cookiecutter.postgres_user}}:{{cookiecutter.postgres_password}}@127.0.0.1:5432/{{cookiecutter.project_slug}}",
    ),
}
DATABASES["default"]["ATOMIC_REQUESTS"] = True

# GitHub Actions sets GITHUB_WORKFLOW; GitLab CI sets GITLAB_CI.
# Keep an explicit sqlite DATABASE_URL (CI when testing is off) — do not force Postgres.
_database_url = os.environ.get("DATABASE_URL", "")
_in_ci = os.environ.get("GITHUB_WORKFLOW") or os.environ.get("GITLAB_CI")
if _in_ci and not _database_url.startswith("sqlite"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "ci"),
            "USER": os.environ.get("POSTGRES_USER", "{{cookiecutter.postgres_user}}"),
            "PASSWORD": os.environ.get(
                "POSTGRES_PASSWORD", "{{cookiecutter.postgres_password}}"
            ),
            "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
            "ATOMIC_REQUESTS": True,
        }
    }
