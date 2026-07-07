#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for arg in "$@"; do
    case "$arg" in
        --no-input|-f|--checkout|--config-file*)
            exec cookiecutter "$ROOT_DIR" "$@"
            ;;
    esac
done

if ! command -v cookiecutter >/dev/null 2>&1; then
    echo "cookiecutter is not installed."
    echo "Install it with: pip install cookiecutter"
    exit 1
fi

if [[ ! -t 0 ]]; then
    exec cookiecutter "$ROOT_DIR" "$@"
fi

exec python3 "$ROOT_DIR/hooks/interactive_prompts.py" "$ROOT_DIR"
