from config.env import env

SOCIAL_AUTH_PROVIDERS: tuple[str, ...] = (
{%- if cookiecutter.use_google_login == "y" %}
    "google",
{%- endif %}
{%- if cookiecutter.use_microsoft_login == "y" %}
    "microsoft",
{%- endif %}
{%- if cookiecutter.use_apple_login == "y" %}
    "apple",
{%- endif %}
)

{%- if cookiecutter.use_google_login == "y" %}
GOOGLE_OAUTH_CLIENT_ID = env("GOOGLE_OAUTH_CLIENT_ID", default="")
{%- endif %}
{%- if cookiecutter.use_microsoft_login == "y" %}
MICROSOFT_OAUTH_CLIENT_ID = env("MICROSOFT_OAUTH_CLIENT_ID", default="")
MICROSOFT_OAUTH_TENANT = env("MICROSOFT_OAUTH_TENANT", default="common")
{%- endif %}
{%- if cookiecutter.use_apple_login == "y" %}
APPLE_OAUTH_CLIENT_ID = env("APPLE_OAUTH_CLIENT_ID", default="")
{%- endif %}
