import logging

from django.db.models.signals import post_delete
from django.dispatch import receiver

from {{cookiecutter.project_slug}}.file_manager.models import ManagedFile

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=ManagedFile)
def delete_file_from_disk_on_model_delete(sender, instance: ManagedFile, **kwargs) -> None:
    """Remove the physical file after the ManagedFile row is deleted."""
    if instance.file:
        try:
            instance.file.delete(save=False)
        except Exception as exc:
            logger.warning(
                "Failed to remove physical file for ManagedFile id=%s path=%s: %s",
                instance.id,
                getattr(instance.file, "name", "unknown"),
                exc,
            )
