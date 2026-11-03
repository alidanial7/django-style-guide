from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import AllowAny

from {{cookiecutter.project_slug}}.common.http.schema import envelope_serializer
from {{cookiecutter.project_slug}}.core.apis.health.health_apis import HealthApi


@extend_schema_view(
    get=extend_schema(
        tags=["site"],
        summary="Site health check",
        responses=envelope_serializer("SiteHealthEnvelope", HealthApi.OutputSerializer),
    )
)
class SiteHealthApiView(HealthApi):
    """Public health probe mounted under ``/api/v1/site/health/`` (scoped surface sample)."""

    permission_classes = [AllowAny]
