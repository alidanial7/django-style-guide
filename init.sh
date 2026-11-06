#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INPLACE=0
INPLACE_FORCE=0
INPLACE_FORCE_TEMPLATE=0
FORWARD=()
for arg in "$@"; do
    case "$arg" in
        --inplace)
            INPLACE=1
            ;;
        --inplace-force)
            INPLACE=1
            INPLACE_FORCE=1
            ;;
        --inplace-force-template)
            INPLACE=1
            INPLACE_FORCE=1
            INPLACE_FORCE_TEMPLATE=1
            ;;
        --no-input|-f|--checkout|--config-file*)
            # Plain cookiecutter path (no inplace flatten). Use the interactive
            # UI / DSG_INPLACE for generate-into-current-directory.
            exec cookiecutter "$ROOT_DIR" "$@"
            ;;
        *)
            FORWARD+=("$arg")
            ;;
    esac
done

if ! command -v cookiecutter >/dev/null 2>&1; then
    echo "cookiecutter is not installed."
    echo "Install it with: pip install cookiecutter"
    exit 1
fi

if [[ ! -t 0 ]]; then
    exec cookiecutter "$ROOT_DIR" "${FORWARD[@]}"
fi

EXTRA_ARGS=()
if [[ "$INPLACE_FORCE_TEMPLATE" -eq 1 ]]; then
    export DSG_INPLACE=1
    export DSG_INPLACE_FORCE=1
    export DSG_INPLACE_FORCE_TEMPLATE=1
    EXTRA_ARGS+=(--inplace-force-template)
elif [[ "$INPLACE_FORCE" -eq 1 ]]; then
    export DSG_INPLACE=1
    export DSG_INPLACE_FORCE=1
    EXTRA_ARGS+=(--inplace-force)
elif [[ "$INPLACE" -eq 1 ]]; then
    export DSG_INPLACE=1
    EXTRA_ARGS+=(--inplace)
fi

exec python3 "$ROOT_DIR/hooks/interactive_prompts.py" "$ROOT_DIR" "${EXTRA_ARGS[@]}"
