"""Client-scoped routes under ``/api/v1/site/``."""

from django.urls import include, path

urlpatterns = [
    path("", include(("{{cookiecutter.project_slug}}.core.urls.site_core_url", "site_core"))),
]
