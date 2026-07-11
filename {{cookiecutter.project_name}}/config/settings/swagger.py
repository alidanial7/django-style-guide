SPECTACULAR_SETTINGS = {
    "TITLE": "{{cookiecutter.project_name}} API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
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
