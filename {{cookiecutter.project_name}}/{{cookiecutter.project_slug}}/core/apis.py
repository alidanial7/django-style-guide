from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthApi(APIView):
    class OutputSerializer(serializers.Serializer):
        status = serializers.CharField()

    @extend_schema(
        tags=["system"],
        summary="Health check",
        responses=OutputSerializer,
    )
    def get(self, request):
        return Response({"status": "ok"})
