REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "{{cookiecutter.project_slug}}.common.http.exception_handler.api_exception_handler",
    # No DEFAULT_FILTER_BACKENDS: plain APIView does not auto-run filter backends.
    # Lists are unfiltered by default; when needed apply django-filter FilterSet in the view.
    # Deny by default — public endpoints must set permission_classes = [AllowAny].
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
{%- if cookiecutter.use_jwt == "y" %}
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
{%- else %}
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.SessionAuthentication",),
{%- endif %}
    "DEFAULT_THROTTLE_RATES": {
        "auth": "20/minute",
        "register": "10/minute",
        "password_reset": "5/minute",
    },
}
