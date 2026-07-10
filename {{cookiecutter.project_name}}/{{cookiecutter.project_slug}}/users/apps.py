from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "{{cookiecutter.project_slug}}.users"

    def ready(self):
        from {{cookiecutter.project_slug}}.users.signals import user_signals  # noqa: F401
