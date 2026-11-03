"""Portal-level DRF permission stubs.

Extend with domain flags / roles as the product grows. Default ``IsAuthenticated``
still applies via ``ApiAuthMixin`` — use these on views that need portal gates.
"""

from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Allow users with ``is_admin`` (maps to Django ``is_staff`` on BaseUser)."""

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "is_admin", False))


class IsCustomer(BasePermission):
    """Allow authenticated non-admin users (simple customer/portal stub)."""

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return not getattr(user, "is_admin", False)
