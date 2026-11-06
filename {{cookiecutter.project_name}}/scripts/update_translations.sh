#!/usr/bin/env bash
# Thin wrapper around: python manage.py update_translations
# Locales come from settings.LANGUAGES (any count) or --locale flags — do not
# hardcode language codes here.
#
# Flags:
#   --compile              compile .po → .mo after updating catalogs
#   --compile-messages     legacy alias for --compile
#   --locale <code>        pass-through (repeatable)
#   --no-clean             pass-through
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [[ -x "$PROJECT_DIR/venv/bin/python" ]]; then
  PYTHON="$PROJECT_DIR/venv/bin/python"
elif [[ -x "$PROJECT_DIR/.venv/bin/python" ]]; then
  PYTHON="$PROJECT_DIR/.venv/bin/python"
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
elif command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
else
  echo "Error: python or python3 not found in PATH." >&2
  exit 1
fi

cd "$PROJECT_DIR"

# Map legacy --compile-messages → --compile. Use ${arr[@]+…} so an empty
# array does not trip `set -u` (bash treats bare "${arr[@]}" as unbound).
ARGS=()
for arg in "$@"; do
  if [[ "$arg" == "--compile-messages" ]]; then
    ARGS+=(--compile)
  else
    ARGS+=("$arg")
  fi
done

exec "$PYTHON" manage.py update_translations ${ARGS[@]+"${ARGS[@]}"}
