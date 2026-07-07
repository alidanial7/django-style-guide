import sys

celery = "{{ cookiecutter.use_celery }}"
rabbitmq = "{{ cookiecutter.use_rabbitmq }}"

if celery == "y" and rabbitmq != "y":
    print()
    print("Celery requires RabbitMQ as the message broker.")
    print("Enable RabbitMQ (use_rabbitmq=y) or disable Celery (use_celery=n).")
    print()
    sys.exit(1)
