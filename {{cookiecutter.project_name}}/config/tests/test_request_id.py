import pytest
from django.http import HttpResponse
from django.test import RequestFactory

from config.request_id import REQUEST_ID_HEADER, RequestIdMiddleware, _request_id_var, get_request_id


def test_request_id_middleware_sets_header():
    def view(request):
        return HttpResponse("ok")

    middleware = RequestIdMiddleware(view)
    request = RequestFactory().get("/")
    response = middleware(request)

    assert REQUEST_ID_HEADER in response
    assert response[REQUEST_ID_HEADER]
    assert request.request_id == response[REQUEST_ID_HEADER]
    assert get_request_id() is None


def test_request_id_middleware_reuses_inbound_header():
    def view(request):
        return HttpResponse("ok")

    middleware = RequestIdMiddleware(view)
    request = RequestFactory().get("/", HTTP_X_REQUEST_ID="inbound-id-42")
    response = middleware(request)

    assert response[REQUEST_ID_HEADER] == "inbound-id-42"
    assert request.request_id == "inbound-id-42"


def test_request_id_middleware_propagates_original_exception():
    def view(request):
        raise RuntimeError("boom")

    middleware = RequestIdMiddleware(view)
    request = RequestFactory().get("/")

    with pytest.raises(RuntimeError, match="boom"):
        middleware(request)

    assert get_request_id() is None
    assert _request_id_var.get() is None
