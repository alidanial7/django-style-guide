import sys

celery = "{{ cookiecutter.use_celery }}"
rabbitmq = "{{ cookiecutter.use_rabbitmq }}"
use_ci = "{{ cookiecutter.use_ci }}"
ci_provider = "{{ cookiecutter.ci_provider }}"

if celery == "y" and rabbitmq != "y":
    print()
    print("  Celery requires RabbitMQ as the message broker.")
    print("  Enable RabbitMQ (use_rabbitmq=y) or disable Celery (use_celery=n).")
    print()
    sys.exit(1)

if use_ci == "y" and ci_provider not in ("github", "gitlab"):
    print()
    print("  CI is enabled but ci_provider is invalid.")
    print("  Set ci_provider to 'github' or 'gitlab' (or set use_ci=n).")
    print()
    sys.exit(1)
