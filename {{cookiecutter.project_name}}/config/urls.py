from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
{%- if cookiecutter.use_i18n == "y" %}
    path("i18n/", include("django.conf.urls.i18n")),
{%- endif %}
    path("api/v1/", include(("{{cookiecutter.project_slug}}.api.urls", "api"))),
]

if settings.DEBUG:
    # OpenAPI / Swagger under /api/docs/ (not `/`).
    # Multi-scope mode: post_gen adds /api/docs/<scope>/ mounts.
    docs_urlpatterns = [
        path("schema/", SpectacularAPIView.as_view(api_version="v1"), name="schema"),
        path("", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ]
    urlpatterns = [
        path("api/docs/", include(docs_urlpatterns)),
        *urlpatterns,
    ]
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]
{%- if cookiecutter.reverse_proxy == "none" %}
else:
    # No reverse proxy: Django serves uploaded media from the volume.
    # Prefer nginx/traefik at generation time for production traffic.
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]
{%- endif %}
