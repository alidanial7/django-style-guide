#!/usr/bin/env bash
set -e

# Pass --compile-messages to compile translation files after updating them.
RUN_COMPILE_MESSAGES=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --compile-messages)
            RUN_COMPILE_MESSAGES=true
            shift
            ;;
        -h|--help)
            echo "Usage: $(basename "$0") [--compile-messages]"
            echo
            echo "  --compile-messages    Run compilemessages after updating translations"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: $(basename "$0") [--compile-messages]" >&2
            exit 1
            ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if command -v python >/dev/null 2>&1; then
    PYTHON=python
elif command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
else
    echo "Error: python or python3 not found in PATH." >&2
    exit 1
fi

for cmd in msgattrib msgcat; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Error: $cmd not found. Install gettext (e.g. brew install gettext)." >&2
        exit 1
    fi
done

if sed --version >/dev/null 2>&1; then
    sed_inplace() { sed -i "$@"; }
else
    sed_inplace() { sed -i '' "$@"; }
fi

MAKEMESSAGES_IGNORE=(
    -i venv
    -i .venv
    -i "*/site-packages/*"
    -i node_modules
    -i staticfiles
    -i media
)

cd "$PROJECT_DIR"

echo ">>> Project dir: $PROJECT_DIR"

if ! find "$PROJECT_DIR" -path "*/locale/*/LC_MESSAGES" -type d -print -quit | grep -q .; then
    DEFAULT_LOCALE="$("$PYTHON" manage.py shell -c "
from django.conf import settings
from django.utils.translation import trans_real
print(trans_real.to_locale(settings.LANGUAGE_CODE))
")"

    echo ">>> No locales found. Bootstrapping default locale: $DEFAULT_LOCALE"

    "$PYTHON" manage.py makemessages -l "$DEFAULT_LOCALE" \
        --no-location \
        --no-wrap \
        "${MAKEMESSAGES_IGNORE[@]}"
fi

echo ">>> Running makemessages..."

"$PYTHON" manage.py makemessages -a \
    --no-location \
    --no-wrap \
    "${MAKEMESSAGES_IGNORE[@]}"

echo ">>> Cleaning po files..."

find "$PROJECT_DIR" \
    -path "*/venv" -prune -o \
    -path "*/.venv" -prune -o \
    -path "*/locale/*/LC_MESSAGES/*.po" -print | while read -r file; do

    echo "Cleaning: $file"

    sed_inplace '/^"POT-Creation-Date:/d' "$file"

    cleaned_file="$(mktemp)"
    msgattrib --no-obsolete -o "$cleaned_file" "$file"
    mv "$cleaned_file" "$file"

    sorted_file="$(mktemp)"
    msgcat --sort-output -o "$sorted_file" "$file"
    mv "$sorted_file" "$file"
done

if [[ "$RUN_COMPILE_MESSAGES" == true ]]; then
    echo ">>> Compiling messages..."

    "$PYTHON" manage.py compilemessages

    echo ">>> Adding POT-Creation-Date (build only)..."

    find "$PROJECT_DIR" \
        -path "*/locale/*/LC_MESSAGES/*.po" -print | while read -r file; do

        NOW="$(date '+%Y-%m-%d %H:%M%z')"

        if ! grep -q 'POT-Creation-Date' "$file"; then
            header_file="$(mktemp)"
            {
                printf '"POT-Creation-Date: %s\\n"\n' "$NOW"
                cat "$file"
            } > "$header_file"
            mv "$header_file" "$file"
        fi
    done

else
    echo ">>> Skipping compilemessages. Pass --compile-messages to run it."
fi

echo ">>> Done."
