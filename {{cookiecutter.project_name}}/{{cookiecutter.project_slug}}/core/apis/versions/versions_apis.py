from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from config.deploy_version import read_deploy_version
from {{cookiecutter.project_slug}}.common.http import api_response
from {{cookiecutter.project_slug}}.common.http.schema import envelope_serializer


class VersionsApi(APIView):
    """Public deploy version probe (CI/Docker ``version.txt``)."""

    permission_classes = [AllowAny]

    class OutputSerializer(serializers.Serializer):
        version = serializers.CharField(
            allow_null=True,
            help_text=(
                "Deployed application version from ``version.txt`` "
                "(Docker build-arg / CI tag or SHA). Null when the file is missing."
            ),
        )

    @extend_schema(
        tags=["system"],
        summary="Deploy version",
        description=(
            "Returns the version baked into the running image via ``version.txt``. "
            "Public by design for clients and ops — no secrets. "
            "Canonical path: ``/api/v1/versions/`` (platform; not under a scope)."
        ),
        responses=envelope_serializer("VersionsEnvelope", OutputSerializer),
    )
    def get(self, request):
        return api_response(data={"version": read_deploy_version()})
