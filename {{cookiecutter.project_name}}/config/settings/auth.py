AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "{{cookiecutter.project_slug}}.users.validators.password.PasswordNumberDjangoValidator",
    },
    {
        "NAME": "{{cookiecutter.project_slug}}.users.validators.password.PasswordLetterDjangoValidator",
    },
    {
        "NAME": "{{cookiecutter.project_slug}}.users.validators.password.PasswordSpecialCharDjangoValidator",
    },
]

AUTH_USER_MODEL = "users.BaseUser"
{%- if cookiecutter.use_jwt != "y" %}

LOGIN_URL = "/api/v1/auth/session/login/"
{%- endif %}
