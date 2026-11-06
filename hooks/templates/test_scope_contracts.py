"""Runtime contracts for multi-scope membership and permissions."""

from __future__ import annotations

import pytest
from django.conf import settings
from django.test import RequestFactory
from django.utils.module_loading import import_string
from rest_framework import status
from rest_framework.test import APIRequestFactory

from config.api_scope import ApiScopeMiddleware, resolve_api_scope
from __PROJECT_SLUG__.users.permissions import IsScopeMember
from __PROJECT_SLUG__.users.services.scope_membership import (
    ensure_scope_membership,
    user_in_scope,
)
from __PROJECT_SLUG__.users.tests.api_urls import api_reverse
from __PROJECT_SLUG__.users.tests.user_factories import BaseUserFactory

# __LOGIN_HELPERS__


@pytest.mark.django_db
class TestScopeContracts:
    def test_middleware_sets_api_scope(self):
        scopes = list(settings.API_SCOPES)
        assert scopes
        scope = scopes[0]
        factory = RequestFactory()
        request = factory.get(f"/api/v1/{scope}/users/me/")
        captured = {}

        def view(req):
            captured["scope"] = getattr(req, "api_scope", None)
            from django.http import HttpResponse

            return HttpResponse("ok")

        ApiScopeMiddleware(view)(request)
        assert captured["scope"] == scope
        assert resolve_api_scope(f"/api/v1/{scope}/auth/login/") == scope
        assert resolve_api_scope("/api/v1/health/") is None

    def test_register_membership_is_scope_local(self, api_client):
        scopes = list(settings.API_SCOPES)
        assert len(scopes) >= 2
        primary, other = scopes[0], scopes[1]
        email = "scope-reg@example.com"
        response = api_client.post(
            api_reverse("users:register", scope=primary),
            data=_register_payload(email=email, suffix="reg"),
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        from __PROJECT_SLUG__.users.models import BaseUser

        user = BaseUser.objects.get(email=email)
        assert user_in_scope(user=user, scope=primary) is True
        assert user_in_scope(user=user, scope=other) is False

    # __JWT_LOGIN_TEST__

    def test_is_scope_member_requires_membership(self):
        scopes = list(settings.API_SCOPES)
        assert scopes
        scope = scopes[0]
        user = BaseUserFactory()
        factory = APIRequestFactory()
        request = factory.get(f"/api/v1/{scope}/users/me/")
        request.user = user
        request.api_scope = scope

        assert IsScopeMember().has_permission(request, None) is False
        ensure_scope_membership(user=user, scope=scope)
        assert IsScopeMember().has_permission(request, None) is True
        assert IsScopeMember.for_scope(scope)().has_permission(request, None) is True

    def test_scoped_schema_generator_exported(self):
        scopes = list(settings.API_SCOPES)
        assert scopes
        scope = scopes[0]
        pascal = "".join(part.capitalize() for part in scope.split("_") if part)
        gen = import_string(
            f"__PROJECT_SLUG__.common.http.schema.{pascal}SchemaGenerator"
        )
        assert gen is not None
