from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FileManagerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "{{cookiecutter.project_slug}}.file_manager"
    verbose_name = _("file manager")

    def ready(self) -> None:
        from {{cookiecutter.project_slug}}.file_manager.signals import file_signals  # noqa: F401
