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
    echo "Containers stay up while this script runs (log follow). Ctrl+C / closing the"
    echo "terminal stops and removes the compose services (volumes are kept unless --clean)."
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

CLEANED_UP=0
cleanup() {
    if [ "$CLEANED_UP" -eq 1 ]; then
        return
    fi
    CLEANED_UP=1
    echo
    echo "Stopping development containers..."
    docker compose -f "$COMPOSE_FILE" down --remove-orphans || true
}

# INT/TERM/HUP: Ctrl+C, kill, terminal/editor close. EXIT: any process end.
trap cleanup EXIT INT TERM HUP

if [ "$CLEAN" = true ]; then
    echo "Cleaning development containers and volumes..."
    docker compose -f "$COMPOSE_FILE" down -v --remove-orphans || true
fi

echo "Starting development containers..."
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans

echo "Waiting for Postgres..."
POSTGRES_READY=false
for _ in $(seq 1 30); do
    if docker compose -f "$COMPOSE_FILE" exec -T db pg_isready -U "{{cookiecutter.postgres_user}}" -d "{{cookiecutter.project_slug}}" >/dev/null 2>&1; then
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
echo "  Postgres   localhost:5432  (PostgreSQL {{cookiecutter.postgres_version}})"
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
echo "Following container logs (Ctrl+C or closing this terminal stops services)..."
docker compose -f "$COMPOSE_FILE" logs -f
