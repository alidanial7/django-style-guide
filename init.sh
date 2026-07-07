#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v cookiecutter >/dev/null 2>&1; then
    echo "cookiecutter is not installed."
    echo "Install it with: pip install cookiecutter"
    exit 1
fi

cat <<'EOF'

  ╔══════════════════════════════════════════════════════════╗
  ║           Django Style Guide — Project Generator         ║
  ║                                                          ║
  ║  HackSoft-inspired structure · Docker Compose · DRF      ║
  ╚══════════════════════════════════════════════════════════╝

  You will be asked a few questions about your project.
  Press Enter to accept the default shown in [brackets].

  Tips:
    • Leave project_slug empty to auto-generate from the project name
    • Celery requires RabbitMQ
    • Sentry only activates when SENTRY_DSN is set in .env

EOF

cookiecutter "$ROOT_DIR" "$@"
