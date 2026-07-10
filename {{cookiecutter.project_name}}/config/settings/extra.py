from config.env import env

APP_DOMAIN = env("APP_DOMAIN", default="http://localhost:8000")
{%- if cookiecutter.use_rabbitmq == "y" %}

RABBITMQ_URL = env(
    "RABBITMQ_URL",
    default=env("CELERY_BROKER_URL", default="amqp://guest:guest@localhost:5672//"),
)
{%- endif %}
