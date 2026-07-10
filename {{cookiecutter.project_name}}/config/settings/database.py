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
if os.environ.get("GITHUB_WORKFLOW") or os.environ.get("GITLAB_CI"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "ci"),
            "USER": os.environ.get("POSTGRES_USER", "{{cookiecutter.postgres_user}}"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "{{cookiecutter.postgres_password}}"),
            "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }
