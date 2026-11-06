MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "config.request_id.RequestIdMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
{%- if cookiecutter.use_i18n == "y" %}
    "django.middleware.locale.LocaleMiddleware",
{%- endif %}
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
{%- if cookiecutter.use_scoped_apis == "y" %}
    "config.api_scope.ApiScopeMiddleware",
{%- endif %}
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
