LOCAL_APPS = [
    "{{cookiecutter.project_slug}}.core.apps.CoreConfig",
    "{{cookiecutter.project_slug}}.common.apps.CommonConfig",
    "{{cookiecutter.project_slug}}.commands.apps.CommandsConfig",
{%- if cookiecutter.use_jwt == "y" %}
    "{{cookiecutter.project_slug}}.users.apps.UsersConfig",
    "{{cookiecutter.project_slug}}.authentication.apps.AuthenticationConfig",
{%- endif %}
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "django_filters",
{%- if cookiecutter.use_celery == "y" %}
    "django_celery_results",
    "django_celery_beat",
{%- endif %}
{%- if cookiecutter.use_jwt == "y" %}
    "rest_framework_simplejwt.token_blacklist",
{%- endif %}
    "corsheaders",
    "drf_spectacular",
    "django_extensions",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    # http://whitenoise.evans.io/en/stable/django.html#using-whitenoise-in-development
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    *THIRD_PARTY_APPS,
    *LOCAL_APPS,
]
