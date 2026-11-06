from config.deploy_version import read_deploy_version

SPECTACULAR_SETTINGS = {
    "TITLE": "{{cookiecutter.project_name}} API",
    # Prefer baked deploy version when present (see version.txt / Docker VERSION).
    "VERSION": read_deploy_version() or "0.0.0-dev",
    "SERVE_INCLUDE_SCHEMA": False,
    # Split request/response components (e.g. FileField binary on request, URI on response).
    "COMPONENT_SPLIT_REQUEST": True,
    # Stable enum component names for OpenAPI codegen — extend as domain enums grow.
    "ENUM_NAME_OVERRIDES": {
        # "ExampleStatusEnum": "{{cookiecutter.project_slug}}.example.enums.ExampleStatus",
    },
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
    },
    "APPEND_COMPONENTS": {
        "schemas": {
            "ApiMessageItem": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "code": {"type": "string"},
                },
                "required": ["message", "code"],
            },
            "ApiErrorEnvelope": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "enum": [False]},
                    "status": {"type": "integer"},
                    "result": {"type": "array", "items": {}},
                    "messages": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/ApiMessageItem"},
                        },
                    },
                },
                "required": ["success", "status", "result", "messages"],
            },
        },
{%- if cookiecutter.use_jwt == "y" %}
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        },
{%- endif %}
    },
}
