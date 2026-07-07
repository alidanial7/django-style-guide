from config.env import env  # noqa

from config.settings.apps import *  # noqa
from config.settings.auth import *  # noqa
from config.settings.cache import *  # noqa
{%- if cookiecutter.use_celery == "y" %}
from config.settings.celery import *  # noqa
{%- endif %}
from config.settings.core import *  # noqa
from config.settings.cors import *  # noqa
from config.settings.database import *  # noqa
from config.settings.drf import *  # noqa
from config.settings.extra import *  # noqa
from config.settings.i18n import *  # noqa
{%- if cookiecutter.use_jwt == "y" %}
from config.settings.jwt import *  # noqa
{%- endif %}
from config.settings.middleware import *  # noqa
from config.settings.security import *  # noqa
from config.settings.sessions import *  # noqa
from config.settings.static_media import *  # noqa
from config.settings.swagger import *  # noqa
from config.settings.templates import *  # noqa
{%- if cookiecutter.use_sentry == "y" %}
from config.settings.sentry import *  # noqa
{%- endif %}
