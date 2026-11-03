from django.urls import path

from {{cookiecutter.project_slug}}.core.apis.site.health import SiteHealthApiView

app_name = "site_core"

urlpatterns = [
    path("health/", SiteHealthApiView.as_view(), name="health"),
]
