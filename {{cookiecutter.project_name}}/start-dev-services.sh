#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="docker-compose.dev.yml"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

usage() {
    echo "Usage: $(basename "$0") [--clean] [--detach|-d]"
    echo
    echo "Start local development infrastructure (Postgres{%- if cookiecutter.use_rabbitmq == "y" %}, RabbitMQ{%- endif %}{%- if cookiecutter.use_redis == "y" %}, Redis{%- endif %}{%- if cookiecutter.use_pgadmin == "y" %}, pgAdmin{%- endif %})."
    echo
    echo "Default: containers stay up while this script runs (log follow). Ctrl+C / closing"
    echo "the terminal stops and removes the compose services (volumes kept unless --clean)."
    echo
    echo "  --detach, -d  Start in the background and exit (containers keep running)"
    echo "  --clean       Stop containers, remove named Postgres volume, wipe ./volumes/* bind mounts"
    echo "  -h, --help    Show this help"
}

CLEAN=false
DETACH=false

for arg in "$@"; do
    case "$arg" in
        --clean) CLEAN=true ;;
        --detach|-d) DETACH=true ;;
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

if [ "$DETACH" = false ]; then
    # INT/TERM/HUP: Ctrl+C, kill, terminal/editor close. EXIT: any process end.
    trap cleanup EXIT INT TERM HUP
fi

if [ "$CLEAN" = true ]; then
    echo "Cleaning development containers, named Postgres volume, and bind mounts..."
    # -v removes named volumes declared in this compose file (postgres_data).
    docker compose -f "$COMPOSE_FILE" down -v --remove-orphans || true
    # Redis/RabbitMQ/pgAdmin still use bind mounts under ./volumes/ —
    # `down -v` does not wipe those host dirs.
    if [ -d volumes ]; then
        for svc_dir in volumes/*/; do
            [ -d "$svc_dir" ] || continue
            find "$svc_dir" -mindepth 1 ! -name '.gitkeep' -exec rm -rf {} + 2>/dev/null || true
        done
        echo "Wiped ./volumes/*/ bind mounts (kept .gitkeep placeholders)."
    fi
    echo "Removed compose named volumes (including postgres_data)."
fi

echo "Starting development containers..."
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans

echo "Waiting for Postgres (database {{cookiecutter.project_slug}})..."
POSTGRES_READY=false
for _ in $(seq 1 30); do
    # Require the app DB to exist — pg_isready alone can pass before init finishes.
    if docker compose -f "$COMPOSE_FILE" exec -T db \
        psql -U "{{cookiecutter.postgres_user}}" -d "{{cookiecutter.project_slug}}" -c 'SELECT 1' >/dev/null 2>&1; then
        POSTGRES_READY=true
        break
    fi
    sleep 1
done

if [ "$POSTGRES_READY" = true ]; then
    echo "Postgres is ready (database {{cookiecutter.project_slug}})."
else
    echo "Warning: database '{{cookiecutter.project_slug}}' is not ready."
    echo "  If this persists, wipe and recreate: ./start-dev-services.sh --clean"
    echo "  Or create it: docker compose -f $COMPOSE_FILE exec db psql -U {{cookiecutter.postgres_user}} -d postgres -c 'CREATE DATABASE {{cookiecutter.project_slug}};'"
fi

echo
echo "Development services are running:"
echo "  Postgres   localhost:5432  (PostgreSQL {{cookiecutter.postgres_version}}; data in Docker volume postgres_data)"
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

if [ "$DETACH" = true ]; then
    echo "Detached. Stop later with: docker compose -f $COMPOSE_FILE down"
    echo "Or: make down"
    exit 0
fi

echo "Following container logs (Ctrl+C or closing this terminal stops services)..."
docker compose -f "$COMPOSE_FILE" logs -f
