"""Unfold admin UI settings.

Shipped only when Unfold is enabled at generation time; `post_gen` removes
this file when the option is off. Parent wires import + INSTALLED_APPS.
"""

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "SITE_TITLE": "{{cookiecutter.project_name}}",
    "SITE_HEADER": "{{cookiecutter.project_name}}",
    "SITE_SYMBOL": "settings",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Navigation"),
                "separator": True,
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                    # Add domain sections here, e.g. users / content.
                    # Prefer reverse_lazy("admin:app_model_changelist") — never hardcode /admin/….
                ],
            },
        ],
    },
}

# Shared Unfold customizations live in this local app (widgets, templates, static).
ADMINISTRATION_APP = "{{cookiecutter.project_slug}}.administration"
