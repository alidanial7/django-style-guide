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
  # `--` so patterns like `--fake` are not parsed as ripgrep flags.
  if rg -F -q -- "$pattern" "$path"; then
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
  if rg -F -q -- "$pattern" "$path"; then
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
assert_file "$OUT/JwtDefaults/config/deploy_version.py"
assert_grep 'versions/' "$OUT/JwtDefaults/jwtdefaults/core/urls/__init__.py"
assert_grep 'class VersionsApi' "$OUT/JwtDefaults/jwtdefaults/core/apis/versions/versions_apis.py"
assert_grep 'ARG VERSION' "$OUT/JwtDefaults/docker/production.Dockerfile"
assert_grep 'version.txt' "$OUT/JwtDefaults/docker/production.Dockerfile"
assert_grep 'VERSION:' "$OUT/JwtDefaults/docker-compose.yml"
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
assert_not_grep '--fake' "$OUT/JwtDefaults/jwtdefaults/commands/management/commands/seed_demo_data.py"
assert_grep 'seed_demo_data' "$OUT/JwtDefaults/docker/dev_entrypoint.sh"
assert_grep 'admin@example.com' "$OUT/JwtDefaults/jwtdefaults/commands/management/commands/seed_demo_data.py"
assert_grep '_seed_local_admin' "$OUT/JwtDefaults/jwtdefaults/commands/management/commands/seed_demo_data.py"
assert_file "$OUT/JwtDefaults/.cursor/rules/commands.mdc"
assert_absent "$OUT/JwtDefaults/.cursor/rules/otp-auth.mdc"
assert_absent "$OUT/JwtDefaults/.cursor/rules/social-auth.mdc"
assert_absent "$OUT/JwtDefaults/jwtdefaults/users/providers"
assert_absent "$OUT/JwtDefaults/config/settings/otp.py"
assert_absent "$OUT/JwtDefaults/config/settings/social_auth.py"
assert_absent "$OUT/JwtDefaults/.cursor/rules/i18n.mdc"
assert_absent "$OUT/JwtDefaults/docs/style-guide/ops/translations.md"
assert_absent "$OUT/JwtDefaults/scripts/update_translations.sh"
assert_absent "$OUT/JwtDefaults/locale"
assert_absent "$OUT/JwtDefaults/jwtdefaults/commands/management/commands/update_translations.py"
assert_grep 'USE_I18N = False' "$OUT/JwtDefaults/config/settings/i18n.py"
assert_not_grep 'LocaleMiddleware' "$OUT/JwtDefaults/config/settings/middleware.py"
assert_not_grep 'django.conf.urls.i18n' "$OUT/JwtDefaults/config/urls.py"

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
assert_grep 'LOCAL_ADMIN_USERNAME = "admin"' "$OUT/UsernameLogin/usernamelogin/commands/management/commands/seed_demo_data.py"
assert_grep 'create_superuser' "$OUT/UsernameLogin/usernamelogin/commands/management/commands/seed_demo_data.py"

gen OtpLogin \
  use_jwt=y use_otp_login=y use_redis=y use_celery=n use_testing=y use_code_style=y use_ci=n
assert_file "$OUT/OtpLogin/.cursor/rules/otp-auth.mdc"
assert_file "$OUT/OtpLogin/otplogin/users/providers/sms/stub.py"
assert_file "$OUT/OtpLogin/otplogin/users/services/otp_services.py"
assert_file "$OUT/OtpLogin/otplogin/users/apis/auth/auth_otp_apis.py"
assert_file "$OUT/OtpLogin/config/settings/otp.py"
assert_grep 'otp/request/' "$OUT/OtpLogin/otplogin/users/urls/auth_url.py"
assert_grep 'phone = models.CharField' "$OUT/OtpLogin/otplogin/users/models/base_user.py"
assert_grep '989134543456' "$OUT/OtpLogin/otplogin/users/validators/phone.py"
assert_grep 'source="user.phone"' "$OUT/OtpLogin/otplogin/users/apis/users/profile/users_profile_serializers.py"
assert_not_grep 'source="user.phone"' "$OUT/JwtDefaults/jwtdefaults/users/apis/users/profile/users_profile_serializers.py"
assert_grep 'OTP_TEST' "$OUT/OtpLogin/.env.example"
assert_grep 'OTP_TEST_CODE = "12345"' "$OUT/OtpLogin/config/settings/otp.py"
assert_grep 'get_sms_provider' "$OUT/OtpLogin/otplogin/users/providers/sms/__init__.py"
assert_grep 'seed_demo_data' "$OUT/OtpLogin/docker/dev_entrypoint.sh"
assert_grep 'hash_register_password' "$OUT/OtpLogin/otplogin/users/services/otp_services.py"
assert_grep 'otp:challenge:{kind}:{phone}' "$OUT/OtpLogin/otplogin/users/services/otp_services.py"
assert_grep 'KIND_PROFILE_UPDATE' "$OUT/OtpLogin/otplogin/users/apis/users/profile/users_profile_apis.py"
assert_grep 'after POST /api/v1/auth/otp/verify/' "$OUT/OtpLogin/otplogin/users/apis/users/register/users_register_serializers.py"
assert_grep 'kind=profile_update' "$OUT/OtpLogin/otplogin/users/apis/users/profile/users_profile_serializers.py"
assert_grep '--detach' "$OUT/OtpLogin/start-dev-services.sh"
assert_grep 'Platform health check' "$OUT/OtpLogin/otplogin/core/apis/health/health_apis.py"
assert_file "$OUT/OtpLogin/docker-compose.dev.yml"
assert_grep 'redis:' "$OUT/OtpLogin/docker-compose.dev.yml"
assert_absent "$OUT/OtpLogin/otplogin/users/providers/social"

echo
echo "==> OtpWithoutRedis (expect pre_gen fail)"
if cookiecutter "$ROOT" --no-input -o "$OUT" project_name="OtpNoRedis" \
  use_jwt=y use_otp_login=y use_redis=n use_celery=n use_testing=y use_code_style=y use_ci=n \
  >/tmp/dsg_otp_noredis.out 2>/tmp/dsg_otp_noredis.err; then
  echo "  FAIL OtpWithoutRedis should have failed pre_gen"
  fail=$((fail + 1))
else
  if rg -F -q -- "Phone OTP requires Redis" /tmp/dsg_otp_noredis.err /tmp/dsg_otp_noredis.out; then
    echo "  OK  pre_gen rejected OTP without Redis"
    pass=$((pass + 1))
  else
    echo "  FAIL missing Redis/OTP error in pre_gen output"
    fail=$((fail + 1))
  fi
fi
assert_absent "$OUT/OtpNoRedis"

gen WithI18n \
  use_jwt=y use_i18n=y use_celery=n use_testing=y use_code_style=y use_ci=n
assert_file "$OUT/WithI18n/.cursor/rules/i18n.mdc"
assert_file "$OUT/WithI18n/docs/style-guide/ops/translations.md"
assert_file "$OUT/WithI18n/scripts/update_translations.sh"
assert_file "$OUT/WithI18n/locale/.gitkeep"
assert_file "$OUT/WithI18n/withi18n/commands/management/commands/update_translations.py"
assert_grep 'USE_I18N = True' "$OUT/WithI18n/config/settings/i18n.py"
assert_grep 'LANGUAGES' "$OUT/WithI18n/config/settings/i18n.py"
assert_grep 'LocaleMiddleware' "$OUT/WithI18n/config/settings/middleware.py"
assert_grep 'django.conf.urls.i18n' "$OUT/WithI18n/config/urls.py"
assert_grep 'LANGUAGE_CODE=en' "$OUT/WithI18n/.env.example"
assert_grep 'update_translations' "$OUT/WithI18n/Makefile"
assert_grep 'update_translations' "$OUT/WithI18n/AGENTS.md"
assert_grep 'Keep rules current' "$OUT/WithI18n/AGENTS.md"
assert_grep 'update_translations' "$OUT/WithI18n/.cursor/rules/commands.mdc"
assert_grep 'LANGUAGE_CODE' "$OUT/WithI18n/.cursor/rules/infra.mdc"

gen SocialLogin \
  use_jwt=y use_google_login=y use_microsoft_login=y use_apple_login=y \
  use_otp_login=n use_celery=n use_testing=y use_code_style=y use_ci=n
assert_file "$OUT/SocialLogin/.cursor/rules/social-auth.mdc"
assert_file "$OUT/SocialLogin/sociallogin/users/providers/social/google.py"
assert_file "$OUT/SocialLogin/sociallogin/users/providers/social/microsoft.py"
assert_file "$OUT/SocialLogin/sociallogin/users/providers/social/apple.py"
assert_file "$OUT/SocialLogin/sociallogin/users/models/social_account.py"
assert_file "$OUT/SocialLogin/sociallogin/users/services/social_auth_services.py"
assert_file "$OUT/SocialLogin/config/settings/social_auth.py"
assert_grep 'social/google/' "$OUT/SocialLogin/sociallogin/users/urls/auth_url.py"
assert_grep 'GOOGLE_OAUTH_CLIENT_ID' "$OUT/SocialLogin/.env.example"
assert_grep 'MICROSOFT_OAUTH_CLIENT_ID' "$OUT/SocialLogin/.env.example"
assert_grep 'APPLE_OAUTH_CLIENT_ID' "$OUT/SocialLogin/.env.example"
assert_grep 'PyJWT' "$OUT/SocialLogin/requirements/base.txt"
assert_grep 'Keep rules current for the next agent' "$OUT/SocialLogin/.cursor/rules/core.mdc"
assert_grep 'password/change' "$OUT/SocialLogin/.cursor/rules/auth.mdc"
assert_grep 'start_domain_app' "$OUT/SocialLogin/.cursor/rules/commands.mdc"
assert_absent "$OUT/SocialLogin/sociallogin/users/providers/sms"

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

gen ScopedKit \
  use_scoped_apis=y api_scopes=admin,factory use_file_manager=y use_unfold_admin=y \
  use_portal_permissions=y \
  infra_repo_name=my-infra-repo \
  use_redis=y use_celery=n use_testing=y use_code_style=y use_ci=n
assert_file "$OUT/ScopedKit/scopedkit/api/admin_urls.py"
assert_file "$OUT/ScopedKit/scopedkit/api/factory_urls.py"
assert_absent "$OUT/ScopedKit/scopedkit/api/site_urls.py"
assert_file "$OUT/ScopedKit/scopedkit/users/models/admin_user.py"
assert_file "$OUT/ScopedKit/scopedkit/users/models/factory_user.py"
assert_grep 'class AdminUser' "$OUT/ScopedKit/scopedkit/users/models/admin_user.py"
assert_grep 'class FactoryUser' "$OUT/ScopedKit/scopedkit/users/models/factory_user.py"
assert_file "$OUT/ScopedKit/scopedkit/users/scope_registry.py"
assert_file "$OUT/ScopedKit/scopedkit/users/services/scope_membership.py"
assert_grep 'class IsScopeMember' "$OUT/ScopedKit/scopedkit/users/permissions.py"
assert_not_grep 'class IsAdminUser' "$OUT/ScopedKit/scopedkit/users/permissions.py"
assert_file "$OUT/ScopedKit/config/api_scope.py"
assert_grep 'ApiScopeMiddleware' "$OUT/ScopedKit/config/settings/middleware.py"
assert_file "$OUT/ScopedKit/scopedkit/commands/management/commands/add_api_scope.py"
assert_file "$OUT/ScopedKit/scopedkit/users/tests/test_scope_contracts.py"
assert_absent "$OUT/ScopedKit/.cursor/rules/portal-permissions.mdc"
assert_file "$OUT/ScopedKit/.cursor/rules/scoped-apis.mdc"
assert_grep 'swagger-ui-admin' "$OUT/ScopedKit/config/urls.py"
assert_grep 'swagger-ui-factory' "$OUT/ScopedKit/config/urls.py"
assert_grep 'AdminSchemaGenerator' "$OUT/ScopedKit/scopedkit/common/http/schema.py"
assert_grep 'ensure_scope_membership_for_request' "$OUT/ScopedKit/scopedkit/users/apis/users/register/users_register_apis.py"
assert_file "$OUT/ScopedKit/scopedkit/file_manager/models/file.py"
assert_file "$OUT/ScopedKit/scopedkit/users/migrations/0002_profile_avatar_managed.py"
assert_grep 'file_manager.ManagedFile' "$OUT/ScopedKit/scopedkit/users/models/profile.py"
assert_grep 'create_managed_file' "$OUT/ScopedKit/scopedkit/users/services/user_services.py"
assert_file "$OUT/ScopedKit/.cursor/rules/file-manager.mdc"
assert_file "$OUT/ScopedKit/docs/style-guide/domain/file-manager.md"
assert_grep 'file_manager/' "$OUT/ScopedKit/docs/style-guide/overview/project-structure.md"
assert_file "$OUT/ScopedKit/scopedkit/administration/apps.py"
assert_file "$OUT/ScopedKit/config/settings/unfold.py"
assert_file "$OUT/ScopedKit/.cursor/rules/unfold-admin.mdc"
assert_grep 'my-infra-repo' "$OUT/ScopedKit/AGENTS.md"
assert_grep 'django-unfold' "$OUT/ScopedKit/requirements/base.txt"
assert_grep 'api/docs/' "$OUT/ScopedKit/config/urls.py"
assert_grep 'api/docs/' "$OUT/JwtDefaults/config/urls.py"
assert_grep 'make_scoped_schema_generator' "$OUT/ScopedKit/scopedkit/common/http/schema.py"

echo
echo "Smoke results: $pass passed, $fail failed"
if [[ "$fail" -gt 0 ]]; then
  exit 1
fi
echo "All smoke asserts passed. Output under $OUT"
