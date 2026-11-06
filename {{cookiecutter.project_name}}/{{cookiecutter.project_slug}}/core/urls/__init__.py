from django.urls import path

from {{cookiecutter.project_slug}}.core.apis.health import HealthApi
from {{cookiecutter.project_slug}}.core.apis.versions import VersionsApi

app_name = "core"

urlpatterns = [
    path("health/", HealthApi.as_view(), name="health"),
    path("versions/", VersionsApi.as_view(), name="versions"),
]
