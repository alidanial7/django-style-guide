"""Custom Unfold admin widgets, forms, mixins, and site-wide admin helpers.

Domain models stay registered in each domain app's ``admin.py`` (prefer
``unfold.admin.ModelAdmin``). Put shared admin customizations here:

- base ``ModelAdmin`` mixins / widgets
- templates under ``templates/administration/``
- static assets under ``static/``

Do not hardcode admin URL paths; use ``reverse`` / ``reverse_lazy`` and
named routes. Mount path remains whatever ``config/urls.py`` configures
(default ``/admin/``).
"""
