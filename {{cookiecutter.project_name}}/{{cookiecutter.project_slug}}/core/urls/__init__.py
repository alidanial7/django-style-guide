from django.urls import path

from {{cookiecutter.project_slug}}.core.apis.health import HealthApi

app_name = "core"

urlpatterns = [
    path("health/", HealthApi.as_view(), name="health"),
]
