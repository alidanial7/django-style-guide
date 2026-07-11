import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def notify_customers(self, message: str) -> None:
    """
    Example Celery task. Prefer domain services for business work; keep tasks thin.

    Replace or remove this sample before production use.
    """
    logger.info("notify_customers: %s", message)
