from __future__ import annotations

import logging

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Model
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException

from {{cookiecutter.project_slug}}.common.db.integrity.parse import parse_integrity_error
from {{cookiecutter.project_slug}}.common.db.integrity.types import IntegrityErrorType
from {{cookiecutter.project_slug}}.common.errors.codes import ErrorCode

logger = logging.getLogger(__name__)


def _field_label(model: type[Model], field_name: str) -> str:
    try:
        return str(model._meta.get_field(field_name).verbose_name)
    except Exception:
        return field_name


def map_integrity_error(error: IntegrityError, *, model: type[Model]) -> None:
    """Raise an API-facing exception for a database integrity failure. Never returns."""
    parsed = parse_integrity_error(error, model=model)

    if parsed.error_type == IntegrityErrorType.UNIQUE:
        if parsed.columns:
            raise ValidationError(
                {
                    field: ValidationError(
                        _("%(field)s already exists.") % {"field": _field_label(model, field)},
                        code=ErrorCode.UNIQUE,
                    )
                    for field in parsed.columns
                }
            )
        raise ValidationError(
            _("A conflicting record already exists."),
            code=ErrorCode.UNIQUE,
        )

    if parsed.error_type == IntegrityErrorType.NOT_NULL:
        if parsed.columns:
            raise ValidationError(
                {
                    field: ValidationError(
                        _("This field cannot be null."),
                        code=ErrorCode.NOT_NULL,
                    )
                    for field in parsed.columns
                }
            )
        raise ValidationError(_("A required database field is missing."), code=ErrorCode.NOT_NULL)

    if parsed.error_type == IntegrityErrorType.FOREIGN_KEY:
        if parsed.columns:
            raise ValidationError(
                {
                    field: ValidationError(
                        _("Invalid reference."),
                        code=ErrorCode.INVALID_REFERENCE,
                    )
                    for field in parsed.columns
                }
            )
        raise ValidationError(_("Invalid reference."), code=ErrorCode.INVALID_REFERENCE)

    logger.exception("Unhandled integrity error for model %s", model.__name__, exc_info=error)
    raise APIException(
        detail=_("Could not complete the request due to a data conflict."),
        code=ErrorCode.UNKNOWN_INTEGRITY,
    )
