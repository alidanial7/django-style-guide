from collections.abc import Sequence
from typing import TYPE_CHECKING

from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
{%- if cookiecutter.use_jwt == "y" %}
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
{%- endif %}


def get_auth_header(headers):
    value = headers.get("Authorization")

    if not value:
        return None

    auth_type, auth_value = value.split()[:2]

    return auth_type, auth_value


if TYPE_CHECKING:
    # This is going to be resolved in the stub library
    # https://github.com/typeddjango/djangorestframework-stubs/
    from rest_framework.permissions import _PermissionClass

    PermissionClassesType = Sequence[_PermissionClass]
else:
    PermissionClassesType = Sequence[type[BasePermission]]


class ApiAuthMixin:
{%- if cookiecutter.use_jwt == "y" %}
    authentication_classes: Sequence[type[BaseAuthentication]] = [
        JWTAuthentication,
    ]
    permission_classes: PermissionClassesType = (IsAuthenticated,)
{%- else %}
    """Opt-in auth mixin. Enable JWT (use_jwt=y) for JWTAuthentication + IsAuthenticated."""

    authentication_classes: Sequence[type[BaseAuthentication]] = []
    permission_classes: PermissionClassesType = ()
{%- endif %}
