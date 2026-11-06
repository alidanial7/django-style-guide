{%- if cookiecutter.use_i18n == "y" %}
import os

from config.env import BASE_DIR, env

LANGUAGE_CODE = env("LANGUAGE_CODE", default="en")

LANGUAGES = [
    ("en", "English"),
    ("fa", "Persian"),
]

USE_I18N = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]
{%- else %}
LANGUAGE_CODE = "en-us"

USE_I18N = False
{%- endif %}

TIME_ZONE = "UTC"
USE_TZ = True
