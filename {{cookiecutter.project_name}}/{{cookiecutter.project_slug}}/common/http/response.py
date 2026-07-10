from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response


def api_response(
    *,
    data=None,
    http_status: int = status.HTTP_200_OK,
    messages: dict | None = None,
) -> Response:
    """
    Success envelope matching the error handler shape:

    {
      "success": true,
      "status": <http_status>,
      "result": <payload>,
      "messages": {}
    }
    """
    return Response(
        {
            "success": True,
            "status": http_status,
            "result": {} if data is None else data,
            "messages": {} if messages is None else messages,
        },
        status=http_status,
    )
