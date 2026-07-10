"""Legacy exception handlers.

Prefer ``common.http.exception_handler.api_exception_handler`` (wired in DRF settings).
"""

from {{cookiecutter.project_slug}}.common.http.exception_handler import api_exception_handler

# Backwards-compatible aliases
drf_default_with_modifications_exception_handler = api_exception_handler
hacksoft_proposed_exception_handler = api_exception_handler
