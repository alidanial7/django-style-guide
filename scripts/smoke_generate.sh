#!/usr/bin/env bash
# Generate option matrices and assert agent-surface / prune expectations.
# No full Django install — fast contributor check.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${SMOKE_OUT:-$ROOT/_gen_smoke}"
export DSG_COOKIECUTTER_SKIP_PROMPT_UI=1

rm -rf "$OUT"
mkdir -p "$OUT"
cd "$ROOT"

pass=0
fail=0

assert_file() {
  local path="$1"
  if [[ -e "$path" ]]; then
    echo "  OK  exists $path"
    pass=$((pass + 1))
  else
    echo "  FAIL missing $path"
    fail=$((fail + 1))
  fi
}

assert_absent() {
  local path="$1"
  if [[ ! -e "$path" ]]; then
    echo "  OK  absent $path"
    pass=$((pass + 1))
  else
    echo "  FAIL still present $path"
    fail=$((fail + 1))
  fi
}

assert_grep() {
  local pattern="$1"
  local path="$2"
  if rg -F -q "$pattern" "$path"; then
    echo "  OK  '$pattern' in $path"
    pass=$((pass + 1))
  else
    echo "  FAIL '$pattern' missing in $path"
    fail=$((fail + 1))
  fi
}

assert_not_grep() {
  local pattern="$1"
  local path="$2"
  if rg -F -q "$pattern" "$path"; then
    echo "  FAIL '$pattern' should not appear in $path"
    fail=$((fail + 1))
  else
    echo "  OK  no '$pattern' in $path"
    pass=$((pass + 1))
  fi
}

gen() {
  local name="$1"
  shift
  echo
  echo "==> $name"
  cookiecutter "$ROOT" --no-input -o "$OUT" project_name="$name" "$@"
}

echo "Validating choice maps…"
python3 hooks/test_choice_context.py

gen JwtDefaults \
  use_jwt=y use_uuid_pk=y use_celery=n use_websockets=n use_redis=n \
  use_sentry=n use_pgadmin=n \
  use_testing=y use_code_style=y use_ci=n reverse_proxy=none
assert_file "$OUT/JwtDefaults/.python-version"
assert_file "$OUT/JwtDefaults/.cursor/rules/core.mdc"
assert_file "$OUT/JwtDefaults/.cursor/rules/testing.mdc"
assert_file "$OUT/JwtDefaults/.cursor/rules/auth.mdc"
assert_absent "$OUT/JwtDefaults/.cursor/rules/celery.mdc"
assert_absent "$OUT/JwtDefaults/docs/style-guide/ops/celery.md"
assert_absent "$OUT/JwtDefaults/.cursor/rules/websockets.mdc"
assert_absent "$OUT/JwtDefaults/.cursor/rules/sentry.mdc"
assert_absent "$OUT/JwtDefaults/.cursor/rules/pgadmin.mdc"
assert_absent "$OUT/JwtDefaults/scripts/bootstrap.sh"
assert_absent "$OUT/JwtDefaults/docker/local.Dockerfile"
assert_grep 'JWT' "$OUT/JwtDefaults/.cursor/rules/auth.mdc"
assert_grep 'UUID PK' "$OUT/JwtDefaults/AGENTS.md"
assert_not_grep 'Celery / tasks' "$OUT/JwtDefaults/AGENTS.md"
assert_file "$OUT/JwtDefaults/jwtdefaults/api/urls.py"
assert_absent "$OUT/JwtDefaults/jwtdefaults/api/apps.py"

gen IntPk \
  use_uuid_pk=n use_jwt=y use_celery=n use_testing=y use_code_style=y use_ci=n
assert_grep 'BigAutoField' "$OUT/IntPk/AGENTS.md"
assert_grep '<int:entity_id>' "$OUT/IntPk/AGENTS.md"
assert_not_grep 'UUID PK' "$OUT/IntPk/AGENTS.md"

gen SessionCelery \
  use_jwt=n use_redis=y use_celery=y celery_broker=redis \
  use_testing=y use_code_style=y reverse_proxy=nginx use_ci=n
assert_file "$OUT/SessionCelery/.cursor/rules/celery.mdc"
assert_file "$OUT/SessionCelery/docs/style-guide/ops/celery.md"
assert_file "$OUT/SessionCelery/docker/nginx"
assert_grep 'session' "$OUT/SessionCelery/.cursor/rules/auth.mdc"
assert_grep 'CELERY_BEAT_SCHEDULE = {}' "$OUT/SessionCelery/config/settings/celery.py"
assert_not_grep 'notify_customers' "$OUT/SessionCelery/config/settings/celery.py"

gen RabbitCelery \
  use_jwt=y use_rabbitmq=y use_redis=n use_celery=y celery_broker=rabbitmq \
  use_testing=y use_code_style=y use_ci=n
assert_file "$OUT/RabbitCelery/.cursor/rules/celery.mdc"
assert_grep 'rabbitmq' "$OUT/RabbitCelery/.cursor/rules/celery.mdc"

gen AsgiWs \
  use_jwt=y use_redis=y use_asgi=y use_websockets=y \
  use_celery=n reverse_proxy=traefik use_testing=y use_code_style=y use_ci=n
assert_file "$OUT/AsgiWs/.cursor/rules/websockets.mdc"
assert_file "$OUT/AsgiWs/docs/style-guide/ops/websockets.md"
assert_file "$OUT/AsgiWs/docker/traefik"

gen NoTest \
  use_testing=n use_code_style=y use_ci=y ci_provider=gitlab use_celery=n
assert_absent "$OUT/NoTest/.cursor/rules/testing.mdc"
assert_absent "$OUT/NoTest/docs/style-guide/ops/testing.md"
assert_absent "$OUT/NoTest/pytest.ini"
assert_file "$OUT/NoTest/.gitlab-ci.yml"
assert_absent "$OUT/NoTest/.github"

gen FlakeOnly \
  use_code_style=n use_testing=y use_ci=n use_celery=n
assert_absent "$OUT/FlakeOnly/.cursor/rules/code-quality.mdc"
assert_file "$OUT/FlakeOnly/.flake8"
assert_absent "$OUT/FlakeOnly/.pre-commit-config.yaml"

gen WithSentryPg \
  use_sentry=y use_pgadmin=y use_celery=n use_testing=y use_code_style=y use_ci=n
assert_file "$OUT/WithSentryPg/.cursor/rules/sentry.mdc"
assert_file "$OUT/WithSentryPg/.cursor/rules/pgadmin.mdc"

# Directory = project_name; package = slugify(project_name)
gen "My-App" \
  use_celery=n use_testing=n use_code_style=y use_ci=n
assert_file "$OUT/My-App/my_app"

echo
echo "Smoke results: $pass passed, $fail failed"
if [[ "$fail" -gt 0 ]]; then
  exit 1
fi
echo "All smoke asserts passed. Output under $OUT"
