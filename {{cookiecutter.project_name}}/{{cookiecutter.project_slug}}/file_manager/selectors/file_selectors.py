from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from {{cookiecutter.project_slug}}.file_manager.models import ManagedFile
from {{cookiecutter.project_slug}}.users.models import BaseUser


def get_managed_file(*, file_id) -> ManagedFile | None:
    """Fetch a single managed file by primary key."""
    try:
        return ManagedFile.objects.select_related("owner").get(id=file_id)
    except (ManagedFile.DoesNotExist, ValueError, ValidationError, TypeError):
        return None


def list_managed_files_for_user(*, user: BaseUser | AnonymousUser) -> QuerySet[ManagedFile]:
    """Return files owned by the authenticated user (empty if anonymous)."""
    if not user or not user.is_authenticated:
        return ManagedFile.objects.none()

    if user.is_superuser or getattr(user, "is_admin", False):
        return ManagedFile.objects.select_related("owner").order_by("-created_at", "-id")

    return (
        ManagedFile.objects.filter(owner=user)
        .select_related("owner")
        .order_by("-created_at", "-id")
    )


def user_can_access_managed_file(
    *,
    user: BaseUser | AnonymousUser | None,
    managed_file: ManagedFile,
    write: bool = False,
) -> bool:
    """Whether ``user`` may read (or write/delete) ``managed_file``."""
    if managed_file.is_public and not write:
        return True

    if not user or not user.is_authenticated:
        return False

    if user.is_superuser or getattr(user, "is_admin", False):
        return True

    return managed_file.owner_id == user.id
