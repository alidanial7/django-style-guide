import os

from config.env import env

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="psql://{{cookiecutter.postgres_user}}:{{cookiecutter.postgres_password}}@127.0.0.1:5432/{{cookiecutter.project_slug}}",
    ),
}
DATABASES["default"]["ATOMIC_REQUESTS"] = True

if os.environ.get("GITHUB_WORKFLOW"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "github_actions",
            "USER": "{{cookiecutter.postgres_user}}",
            "PASSWORD": "{{cookiecutter.postgres_password}}",
            "HOST": "127.0.0.1",
            "PORT": "5432",
        }
    }
