LOCAL_APPS = [
    "{{cookiecutter.project_slug}}.core.apps.CoreConfig",
    "{{cookiecutter.project_slug}}.common.apps.CommonConfig",
    "{{cookiecutter.project_slug}}.commands.apps.CommandsConfig",
    "{{cookiecutter.project_slug}}.users.apps.UsersConfig",
{%- if cookiecutter.use_file_manager == "y" %}
    "{{cookiecutter.project_slug}}.file_manager.apps.FileManagerConfig",
{%- endif %}
{%- if cookiecutter.use_unfold_admin == "y" %}
    "{{cookiecutter.project_slug}}.administration.apps.AdministrationConfig",
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
{%- if cookiecutter.use_websockets == "y" %}
    "channels",
{%- endif %}
    "corsheaders",
    "drf_spectacular",
    "django_extensions",
]

INSTALLED_APPS = [
{%- if cookiecutter.use_unfold_admin == "y" %}
    # Unfold must precede django.contrib.admin
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
{%- endif %}
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
