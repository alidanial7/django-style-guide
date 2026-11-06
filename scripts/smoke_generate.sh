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
assert_absent "$OUT/JwtDefaults/jwtdefaults/users/migrations/0002_profile_avatar_managed.py"
assert_grep 'models.ImageField' "$OUT/JwtDefaults/jwtdefaults/users/models/profile.py"
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
assert_absent "$OUT/JwtDefaults/jwtdefaults/file_manager"
assert_absent "$OUT/JwtDefaults/jwtdefaults/api/site_urls.py"
assert_absent "$OUT/JwtDefaults/jwtdefaults/administration"
assert_absent "$OUT/JwtDefaults/jwtdefaults/users/permissions.py"
assert_grep 'model_delete' "$OUT/JwtDefaults/jwtdefaults/common/services.py"
assert_grep 'paginated_envelope_serializer' "$OUT/JwtDefaults/jwtdefaults/common/http/schema.py"
assert_grep 'ENUM_NAME_OVERRIDES' "$OUT/JwtDefaults/config/settings/swagger.py"
assert_file "$OUT/JwtDefaults/jwtdefaults/commands/management/commands/seed_demo_data.py"
assert_file "$OUT/JwtDefaults/jwtdefaults/commands/management/commands/initial_system.py"

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
assert_grep 'redis://localhost:6379/3' "$OUT/SessionCelery/config/settings/celery.py"
assert_grep 'redis://localhost:6379/0' "$OUT/SessionCelery/config/settings/cache.py"

gen RabbitCelery \
  use_jwt=y use_rabbitmq=y use_redis=n use_celery=y celery_broker=rabbitmq \
  use_testing=y use_code_style=y use_ci=n
assert_file "$OUT/RabbitCelery/.cursor/rules/celery.mdc"
assert_grep 'rabbitmq' "$OUT/RabbitCelery/.cursor/rules/celery.mdc"
assert_file "$OUT/RabbitCelery/docker/rabbitmq/rabbitmq.conf"
assert_grep './volumes/rabbitmq' "$OUT/RabbitCelery/docker-compose.dev.yml"
assert_grep 'transient_nonexcl_queues' "$OUT/RabbitCelery/docker/rabbitmq/rabbitmq.conf"
assert_grep './volumes/postgres' "$OUT/RabbitCelery/docker-compose.dev.yml"
assert_absent "$OUT/RabbitCelery/volumes/redis"

gen UsernameLogin \
  use_jwt=y user_login_field=username use_celery=n use_testing=y use_code_style=y use_ci=n
assert_grep 'USERNAME_FIELD = "username"' "$OUT/UsernameLogin/usernamelogin/users/models/base_user.py"
assert_grep 'username = serializers.CharField' "$OUT/UsernameLogin/usernamelogin/users/apis/users/register/users_register_serializers.py"

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

gen JoytoLike \
  use_scoped_apis=y use_file_manager=y use_unfold_admin=y use_portal_permissions=y \
  infra_repo_name=my-infra-repo \
  use_redis=y use_celery=n use_testing=y use_code_style=y use_ci=n
assert_file "$OUT/JoytoLike/joytolike/api/site_urls.py"
assert_file "$OUT/JoytoLike/joytolike/core/apis/site/health/site_health_apis.py"
assert_file "$OUT/JoytoLike/joytolike/file_manager/models/file.py"
assert_file "$OUT/JoytoLike/joytolike/users/migrations/0002_profile_avatar_managed.py"
assert_grep 'file_manager.ManagedFile' "$OUT/JoytoLike/joytolike/users/models/profile.py"
assert_grep 'create_managed_file' "$OUT/JoytoLike/joytolike/users/services/user_services.py"
assert_file "$OUT/JoytoLike/.cursor/rules/file-manager.mdc"
assert_file "$OUT/JoytoLike/docs/style-guide/domain/file-manager.md"
assert_grep 'file_manager/' "$OUT/JoytoLike/docs/style-guide/overview/project-structure.md"
assert_file "$OUT/JoytoLike/joytolike/administration/apps.py"
assert_file "$OUT/JoytoLike/config/settings/unfold.py"
assert_file "$OUT/JoytoLike/.cursor/rules/unfold-admin.mdc"
assert_file "$OUT/JoytoLike/joytolike/users/permissions.py"
assert_file "$OUT/JoytoLike/.cursor/rules/portal-permissions.mdc"
assert_grep 'my-infra-repo' "$OUT/JoytoLike/AGENTS.md"
assert_grep 'django-unfold' "$OUT/JoytoLike/requirements/base.txt"
assert_grep 'SiteSchemaGenerator' "$OUT/JoytoLike/config/urls.py"

echo
echo "Smoke results: $pass passed, $fail failed"
if [[ "$fail" -gt 0 ]]; then
  exit 1
fi
echo "All smoke asserts passed. Output under $OUT"
