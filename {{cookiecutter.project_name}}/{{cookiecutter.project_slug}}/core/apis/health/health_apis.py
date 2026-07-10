from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.views import APIView

from {{cookiecutter.project_slug}}.common.http import api_response
from {{cookiecutter.project_slug}}.core.services.health_checks import run_health_checks


class ComponentHealthSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["ok", "error"])
    latency_ms = serializers.FloatField(required=False)
    version = serializers.CharField(required=False)


class HealthApi(APIView):
    class OutputSerializer(serializers.Serializer):
        status = serializers.ChoiceField(choices=["ok", "error"])
        checks = serializers.DictField(child=ComponentHealthSerializer())

    @extend_schema(
        tags=["system"],
        summary="Health check",
        description=(
            "Reports Django, database"
            "{% if cookiecutter.use_redis == 'y' %}, Redis{% endif %}"
            "{% if cookiecutter.use_rabbitmq == 'y' %}, RabbitMQ{% endif %}"
            "{% if cookiecutter.use_celery == 'y' %}, and Celery{% endif %}"
            " status without leaking hostnames, credentials, or DEBUG flags. "
            "Returns HTTP 503 when any enabled dependency is unavailable."
        ),
        responses=OutputSerializer,
    )
    def get(self, request):
        payload = run_health_checks()
        http_status = status.HTTP_200_OK if payload["status"] == "ok" else status.HTTP_503_SERVICE_UNAVAILABLE
        return api_response(data=payload, http_status=http_status)
