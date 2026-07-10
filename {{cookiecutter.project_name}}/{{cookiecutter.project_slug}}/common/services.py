from typing import Any

from django.db import IntegrityError, transaction

from {{cookiecutter.project_slug}}.common.db.integrity import map_integrity_error
from {{cookiecutter.project_slug}}.common.types import DjangoModelType


def model_create(*, model_class: type[DjangoModelType], data: dict[str, Any]) -> DjangoModelType:
    try:
        with transaction.atomic():
            instance = model_class(**data)
            instance.full_clean()
            instance.save()
    except IntegrityError as error:
        map_integrity_error(error, model=model_class)
        raise
    return instance


def model_save(*, instance: DjangoModelType, update_fields: list[str] | None = None) -> DjangoModelType:
    try:
        with transaction.atomic():
            instance.full_clean()
            if update_fields is None:
                instance.save()
            else:
                instance.save(update_fields=update_fields)
    except IntegrityError as error:
        map_integrity_error(error, model=instance.__class__)
        raise
    return instance


def model_update(*, instance: DjangoModelType, fields: list[str], data: dict[str, Any]) -> tuple[DjangoModelType, bool]:
    """
    Generic update service meant to be reused in local update services.

    Return value: Tuple with the following elements:
        1. The instance we updated
        2. A boolean value representing whether we performed an update or not.
    """
    has_updated = False

    for field in fields:
        if field not in data:
            continue

        if getattr(instance, field) != data[field]:
            has_updated = True
            setattr(instance, field, data[field])

    if has_updated:
        model_save(instance=instance, update_fields=fields)

    return instance, has_updated
