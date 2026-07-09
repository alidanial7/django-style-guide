#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="docker-compose.dev.yml"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

usage() {
    echo "Usage: $(basename "$0") [--clean]"
    echo
    echo "Start local development infrastructure (Postgres{%- if cookiecutter.use_rabbitmq == "y" %}, RabbitMQ{%- endif %}{%- if cookiecutter.use_redis == "y" %}, Redis{%- endif %}{%- if cookiecutter.use_pgadmin == "y" %}, pgAdmin{%- endif %})."
    echo
    echo "  --clean   Stop containers and remove named volumes (fresh database state)"
    echo "  -h, --help  Show this help"
}

CLEAN=false

for arg in "$@"; do
    case "$arg" in
        --clean) CLEAN=true ;;
        -h|--help) usage; exit 0 ;;
        *)
            echo "Unknown argument: $arg" >&2
            usage >&2
            exit 1
            ;;
    esac
done

if ! command -v docker >/dev/null 2>&1; then
    echo "Error: docker is not installed or not in PATH." >&2
    exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
    echo "Error: docker compose plugin is not available." >&2
    exit 1
fi

if [ ! -f .env ]; then
    echo "Warning: .env not found. Copy .env.example to .env before running Django."
fi

if [ "$CLEAN" = true ]; then
    echo "Cleaning development containers and volumes..."
    docker compose -f "$COMPOSE_FILE" down -v --remove-orphans || true
fi

echo "Starting development containers..."
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans

echo "Waiting for Postgres..."
POSTGRES_READY=false
for _ in $(seq 1 30); do
    if docker compose -f "$COMPOSE_FILE" exec -T db pg_isready -U "{{cookiecutter.postgres_user}}" >/dev/null 2>&1; then
        POSTGRES_READY=true
        break
    fi
    sleep 1
done

if [ "$POSTGRES_READY" = true ]; then
    echo "Postgres is ready."
else
    echo "Warning: Postgres did not become ready in time. Containers are still running."
fi

echo
echo "Development services are running:"
echo "  Postgres   localhost:5432  (PostgreSQL 17.10)"
{%- if cookiecutter.use_redis == "y" %}
echo "  Redis      localhost:6379  (Redis 7.4.9)"
{%- endif %}
{%- if cookiecutter.use_rabbitmq == "y" %}
echo "  RabbitMQ   localhost:5672"
{%- endif %}
{%- if cookiecutter.use_pgadmin == "y" %}
echo "  pgAdmin    http://localhost:5050"
{%- endif %}
echo
echo "Run Django locally with:"
echo "  python manage.py migrate"
echo "  python manage.py runserver"
echo
echo "Following container logs (Ctrl+C stops log follow only)..."
docker compose -f "$COMPOSE_FILE" logs -f
