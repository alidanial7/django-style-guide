#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Pass-through for non-interactive / extra cookiecutter flags
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

if [[ -t 1 ]]; then
    BOLD='\033[1m'
    DIM='\033[2m'
    CYAN='\033[36m'
    GREEN='\033[32m'
    YELLOW='\033[33m'
    MAGENTA='\033[35m'
    RESET='\033[0m'
else
    BOLD='' DIM='' CYAN='' GREEN='' YELLOW='' MAGENTA='' RESET=''
fi

print_banner() {
    echo
    echo -e "${CYAN}${BOLD}  ╔══════════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${CYAN}${BOLD}  ║         Django Style Guide — Project Generator               ║${RESET}"
    echo -e "${CYAN}${BOLD}  ║                                                              ║${RESET}"
    echo -e "${CYAN}${BOLD}  ║   HackSoft structure  ·  Docker Compose  ·  DRF  ·  Celery   ║${RESET}"
    echo -e "${CYAN}${BOLD}  ╚══════════════════════════════════════════════════════════════╝${RESET}"
    echo
    echo -e "${DIM}  Press ${RESET}${BOLD}Enter${RESET}${DIM} for defaults · type ${RESET}${BOLD}y${RESET}${DIM} or ${RESET}${BOLD}n${RESET}${DIM} · Celery needs RabbitMQ${RESET}"
    echo
}

print_section() {
    echo
    echo -e "${MAGENTA}${BOLD}  ── $1 ──${RESET}"
    echo
}

slugify() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/_/g' | sed -E 's/^_|_$//g'
}

prompt_text() {
    local label="$1"
    local default="$2"
    local value

    echo -e "  ${BOLD}${label}${RESET}"
    if [[ -n "$default" ]]; then
        echo -ne "  ${DIM}›${RESET} [${GREEN}${default}${RESET}]: "
    else
        echo -ne "  ${DIM}›${RESET} "
    fi
    read -r value
    if [[ -z "$value" ]]; then
        value="$default"
    fi
    printf '%s' "$value"
}

prompt_yn() {
    local label="$1"
    local help="$2"
    local default="${3:-y}"
    local other
    local input
    local result

    if [[ "$default" == "y" ]]; then
        other="n"
    else
        other="y"
    fi

    echo -e "  ${BOLD}${label}${RESET}"
    if [[ -n "$help" ]]; then
        echo -e "  ${DIM}${help}${RESET}"
    fi
    echo
    if [[ "$default" == "y" ]]; then
        echo -e "    ${GREEN}${BOLD}Y${RESET}  Yes ${DIM}(default)${RESET}"
        echo -e "    ${DIM}N${RESET}  No"
    else
        echo -e "    ${DIM}Y${RESET}  Yes"
        echo -e "    ${GREEN}${BOLD}N${RESET}  No ${DIM}(default)${RESET}"
    fi
    echo
    echo -ne "  ${DIM}›${RESET} [${GREEN}${default}${RESET}/${other}]: "
    read -r input

    input="$(echo "$input" | tr '[:upper:]' '[:lower:]' | xargs)"
    case "$input" in
        y|yes|1) result="y" ;;
        n|no|2) result="n" ;;
        "")
            result="$default"
            ;;
        *)
            echo -e "  ${YELLOW}! invalid input, using default: ${default}${RESET}"
            result="$default"
            ;;
    esac

    echo "$result"
}

prompt_license() {
    local input
    local choice="MIT"

    echo -e "  ${BOLD}License${RESET}"
    echo -e "  ${DIM}Choose a license for the generated project.${RESET}"
    echo
    echo -e "    ${GREEN}${BOLD}1${RESET}  MIT ${DIM}(default)${RESET}"
    echo -e "    ${DIM}2${RESET}  BEER"
    echo -e "    ${DIM}3${RESET}  None ${DIM}(no LICENSE file)${RESET}"
    echo
    echo -ne "  ${DIM}›${RESET} [${GREEN}1${RESET}/2/3]: "
    read -r input

    input="$(echo "$input" | tr '[:upper:]' '[:lower:]' | xargs)"
    case "$input" in
        1|mit|"") choice="MIT" ;;
        2|beer) choice="BEER" ;;
        3|none) choice="None" ;;
        *)
            echo -e "  ${YELLOW}! invalid input, using MIT${RESET}"
            choice="MIT"
            ;;
    esac

    echo "$choice"
}

print_banner

print_section "Project"
PROJECT_NAME="$(prompt_text "Project name" "MyProject")"
DEFAULT_SLUG="$(slugify "$PROJECT_NAME")"
PROJECT_SLUG="$(prompt_text "Project slug (Python package)" "$DEFAULT_SLUG")"
[[ -z "$PROJECT_SLUG" ]] && PROJECT_SLUG="$DEFAULT_SLUG"

print_section "Author"
FIRST_NAME="$(prompt_text "First name" "author")"
LAST_NAME="$(prompt_text "Last name" "author lastname")"

print_section "License"
LICENSE="$(prompt_license)"

print_section "Database defaults"
POSTGRES_USER="$(prompt_text "PostgreSQL user" "user")"
POSTGRES_PASSWORD="$(prompt_text "PostgreSQL password" "password")"

print_section "Features"
echo -e "  ${DIM}Toggle optional components for your project.${RESET}"
echo

USE_JWT="$(prompt_yn "JWT authentication" "Users app, authentication app, and JWT settings." "y")"
USE_SENTRY="$(prompt_yn "Sentry monitoring" "Adds sentry-sdk. Only active when SENTRY_DSN is set in .env." "n")"
USE_VSCODE="$(prompt_yn "VS Code configuration" "Adds .vscode settings and recommended extensions." "n")"
USE_PGADMIN="$(prompt_yn "pgAdmin (dev)" "Database UI at http://localhost:5050 in dev Docker Compose." "n")"
USE_REDIS="$(prompt_yn "Redis" "Dev Docker service and django-redis cache backend." "n")"
USE_RABBITMQ="$(prompt_yn "RabbitMQ" "Message broker in Docker Compose. Required for Celery." "n")"
USE_CELERY="$(prompt_yn "Celery" "Background tasks: worker + beat in production Docker Compose." "n")"
USE_CODE_STYLE="$(prompt_yn "Code style tooling" "Ruff + pre-commit git hooks (replaces flake8-only setup)." "n")"

if [[ "$USE_CELERY" == "y" && "$USE_RABBITMQ" != "y" ]]; then
    echo
    echo -e "  ${YELLOW}↳ Celery requires RabbitMQ — RabbitMQ will be enabled.${RESET}"
    USE_RABBITMQ="y"
fi

print_section "Summary"
echo -e "  ${BOLD}Project${RESET}     ${PROJECT_NAME} ${DIM}(${PROJECT_SLUG})${RESET}"
echo -e "  ${BOLD}License${RESET}     ${LICENSE}"
echo -e "  ${BOLD}Features${RESET}    jwt=${USE_JWT}  sentry=${USE_SENTRY}  vscode=${USE_VSCODE}  pgadmin=${USE_PGADMIN}"
echo -e "              redis=${USE_REDIS}  rabbitmq=${USE_RABBITMQ}  celery=${USE_CELERY}  code_style=${USE_CODE_STYLE}"
echo
echo -ne "  ${DIM}›${RESET} Generate project? [${GREEN}Y${RESET}/n]: "
read -r confirm
confirm="$(echo "${confirm:-y}" | tr '[:upper:]' '[:lower:]' | xargs)"
if [[ "$confirm" == "n" || "$confirm" == "no" ]]; then
    echo -e "  ${DIM}Cancelled.${RESET}"
    exit 0
fi

echo
echo -e "${CYAN}${BOLD}  Generating project...${RESET}"
echo

cookiecutter "$ROOT_DIR" --no-input \
    project_name="$PROJECT_NAME" \
    project_slug="$PROJECT_SLUG" \
    first_name="$FIRST_NAME" \
    last_name="$LAST_NAME" \
    license="$LICENSE" \
    postgres_user="$POSTGRES_USER" \
    postgres_password="$POSTGRES_PASSWORD" \
    use_jwt="$USE_JWT" \
    use_sentry="$USE_SENTRY" \
    use_vscode="$USE_VSCODE" \
    use_pgadmin="$USE_PGADMIN" \
    use_redis="$USE_REDIS" \
    use_rabbitmq="$USE_RABBITMQ" \
    use_celery="$USE_CELERY" \
    use_code_style="$USE_CODE_STYLE"

echo
echo -e "${GREEN}${BOLD}  ✓ Done!${RESET}  ${DIM}cd ${PROJECT_NAME} && see README.md${RESET}"
echo
