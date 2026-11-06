import os
import re
import shutil
import subprocess
from pathlib import Path

license_choice = "{{cookiecutter.license}}"
jwt = "{{cookiecutter.use_jwt}}"
use_otp_login = "{{cookiecutter.use_otp_login}}"
use_google_login = "{{cookiecutter.use_google_login}}"
use_microsoft_login = "{{cookiecutter.use_microsoft_login}}"
use_apple_login = "{{cookiecutter.use_apple_login}}"
use_i18n = "{{cookiecutter.use_i18n}}"
sentry = "{{cookiecutter.use_sentry}}"
vscode = "{{cookiecutter.use_vscode}}"
code_style = "{{cookiecutter.use_code_style}}"
testing = "{{cookiecutter.use_testing}}"
celery = "{{cookiecutter.use_celery}}"
use_ci = "{{cookiecutter.use_ci}}"
ci_provider = "{{cookiecutter.ci_provider}}"
use_websockets = "{{cookiecutter.use_websockets}}"
use_pgadmin = "{{cookiecutter.use_pgadmin}}"
use_scoped_apis = "{{cookiecutter.use_scoped_apis}}"
api_scopes = "{{cookiecutter.api_scopes}}"
use_file_manager = "{{cookiecutter.use_file_manager}}"
use_unfold_admin = "{{cookiecutter.use_unfold_admin}}"
use_portal_permissions = "{{cookiecutter.use_portal_permissions}}"
use_rabbitmq = "{{cookiecutter.use_rabbitmq}}"
use_redis = "{{cookiecutter.use_redis}}"
reverse_proxy = "{{cookiecutter.reverse_proxy}}"
project_slug = "{{cookiecutter.project_slug}}"


def delete_resource(resource):
    if os.path.isfile(resource):
        print(f"  - removed {resource}")
        os.remove(resource)
    elif os.path.isdir(resource):
        print(f"  - removed {resource}/")
        shutil.rmtree(resource)


def collapse_extra_blank_lines() -> None:
    """Jinja conditionals often leave 3+ newlines; keep at most one blank line."""
    skip_parts = {".git", ".venv", "venv", "node_modules", "__pycache__", "migrations"}
    for path in Path(".").rglob("*.py"):
        if skip_parts.intersection(path.parts):
            continue
        original = path.read_text(encoding="utf-8")
        updated = re.sub(r"\n{3,}", "\n\n", original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")


def maybe_run_ruff() -> None:
    """If ruff is on PATH, autofix import/format so generated CI starts green."""
    if code_style != "y":
        return
    ruff = shutil.which("ruff")
    if not ruff:
        return
    subprocess.run([ruff, "check", "--fix", "."], check=False)
    subprocess.run([ruff, "format", "."], check=False)


print()
print("Customizing generated project...")

if license_choice == "None":
    delete_resource("LICENSE")
if jwt == "n":
    delete_resource(f"{project_slug}/users/apis/auth/auth_jwt_apis.py")
    delete_resource(f"{project_slug}/users/apis/auth/auth_logout_apis.py")
    delete_resource(f"{project_slug}/users/apis/auth/tests/test_auth_jwt.py")
    delete_resource("config/settings/jwt.py")
else:
    delete_resource(f"{project_slug}/users/apis/auth/auth_session_apis.py")
    delete_resource(f"{project_slug}/users/apis/auth/tests/test_auth_session.py")
if use_otp_login == "n":
    delete_resource(f"{project_slug}/users/providers/sms")
    delete_resource(f"{project_slug}/users/services/otp_services.py")
    delete_resource(f"{project_slug}/users/validators/phone.py")
    delete_resource(f"{project_slug}/users/validators/tests/test_phone_validators.py")
    delete_resource(f"{project_slug}/users/apis/auth/auth_otp_apis.py")
    delete_resource(f"{project_slug}/users/apis/auth/tests/test_auth_otp.py")
    delete_resource("config/settings/otp.py")
    delete_resource(".cursor/rules/otp-auth.mdc")
_social_any = (
    use_google_login == "y" or use_microsoft_login == "y" or use_apple_login == "y"
)
if not _social_any:
    delete_resource(f"{project_slug}/users/providers/social")
    delete_resource(f"{project_slug}/users/services/social_auth_services.py")
    delete_resource(f"{project_slug}/users/models/social_account.py")
    delete_resource(f"{project_slug}/users/apis/auth/auth_social_apis.py")
    delete_resource(f"{project_slug}/users/apis/auth/tests/test_auth_social.py")
    delete_resource("config/settings/social_auth.py")
    delete_resource(".cursor/rules/social-auth.mdc")
else:
    if use_google_login != "y":
        delete_resource(f"{project_slug}/users/providers/social/google.py")
    if use_microsoft_login != "y":
        delete_resource(f"{project_slug}/users/providers/social/microsoft.py")
    if use_apple_login != "y":
        delete_resource(f"{project_slug}/users/providers/social/apple.py")
if use_otp_login != "y" and not _social_any:
    delete_resource(f"{project_slug}/users/providers")
if use_i18n != "y":
    delete_resource("scripts/update_translations.sh")
    delete_resource(f"{project_slug}/commands/management/commands/update_translations.py")
    delete_resource("locale")
    delete_resource("docs/style-guide/ops/translations.md")
    delete_resource(".cursor/rules/i18n.mdc")
if sentry == "n":
    delete_resource("config/settings/sentry.py")
    delete_resource(".cursor/rules/sentry.mdc")
if use_pgadmin != "y":
    delete_resource(".cursor/rules/pgadmin.mdc")
    delete_resource("volumes/pgadmin")
if use_rabbitmq != "y":
    delete_resource("docker/rabbitmq")
    delete_resource("volumes/rabbitmq")
if use_redis != "y":
    delete_resource("volumes/redis")
if vscode == "n":
    delete_resource(".vscode")
if code_style == "n":
    delete_resource("pyproject.toml")
    delete_resource(".pre-commit-config.yaml")
    delete_resource("setup.cfg")
    delete_resource(".cursor/rules/code-quality.mdc")
else:
    delete_resource(".flake8")
    delete_resource("setup.cfg")
if celery == "n":
    delete_resource("config/celery.py")
    delete_resource("config/tasks.py")
    delete_resource("config/settings/celery.py")
    delete_resource("docker/celery_entrypoint.sh")
    delete_resource("docker/beats_entrypoint.sh")
    delete_resource("scripts/run_celery_worker.sh")
    delete_resource("scripts/run_celery_beat.sh")
    delete_resource("docs/style-guide/ops/celery.md")
    delete_resource(".cursor/rules/celery.mdc")
if use_websockets != "y":
    delete_resource("config/settings/channels.py")
    delete_resource(f"{project_slug}/core/routing.py")
    delete_resource("docs/style-guide/ops/websockets.md")
    delete_resource(".cursor/rules/websockets.mdc")
if reverse_proxy != "nginx":
    delete_resource("docker/nginx")
if reverse_proxy != "traefik":
    delete_resource("docker/traefik")
if testing == "n":
    delete_resource("pytest.ini")
    delete_resource("config/django/test.py")
    delete_resource(f"{project_slug}/conftest.py")
    delete_resource("docs/style-guide/ops/testing.md")
    delete_resource(".cursor/rules/testing.mdc")
    root = Path(".")
    for path in root.rglob("conftest.py"):
        delete_resource(str(path))
    for path in root.rglob("tests"):
        if path.is_dir():
            delete_resource(str(path))
    for path in root.rglob("*_factories.py"):
        if path.is_file():
            delete_resource(str(path))

# Always remove legacy hardcoded site sample (scopes are scaffolded dynamically).
delete_resource(f"{project_slug}/api/site_urls.py")
delete_resource(f"{project_slug}/core/urls/site_core_url.py")
delete_resource(f"{project_slug}/core/apis/site")

if use_scoped_apis == "y":
    import sys

    # Cookiecutter runs this hook from a temp copy, so __file__ is not hooks/.
    repo_hooks = Path(r"{{ cookiecutter._repo_dir }}") / "hooks"
    if str(repo_hooks) not in sys.path:
        sys.path.insert(0, str(repo_hooks))
    from scope_scaffold import scaffold_scopes

    scaffold_scopes(
        project_root=Path(".").resolve(),
        project_slug=project_slug,
        api_scopes_raw=api_scopes,
        use_file_manager=use_file_manager == "y",
        use_i18n=use_i18n == "y",
        reverse_proxy=reverse_proxy,
        use_testing=testing == "y",
        use_jwt=jwt == "y",
        user_login_field="{{ cookiecutter.user_login_field }}",
    )
    # Scope mode ships IsScopeMember instead of legacy portal stubs.
    delete_resource(".cursor/rules/portal-permissions.mdc")
elif use_portal_permissions != "y":
    delete_resource(f"{project_slug}/users/permissions.py")
    delete_resource(".cursor/rules/portal-permissions.mdc")

if use_file_manager != "y":
    delete_resource(f"{project_slug}/file_manager")
    delete_resource(f"{project_slug}/users/migrations/0002_profile_avatar_managed.py")
    delete_resource("docs/style-guide/domain/file-manager.md")
    delete_resource(".cursor/rules/file-manager.mdc")

if use_unfold_admin != "y":
    delete_resource("config/settings/unfold.py")
    delete_resource(f"{project_slug}/administration")
    delete_resource("docs/style-guide/ops/admin-unfold.md")
    delete_resource(".cursor/rules/unfold-admin.mdc")

if use_ci != "y":
    delete_resource(".github")
    delete_resource(".gitlab-ci.yml")
elif ci_provider == "github":
    delete_resource(".gitlab-ci.yml")
elif ci_provider == "gitlab":
    delete_resource(".github")
else:
    delete_resource(".github")
    delete_resource(".gitlab-ci.yml")

collapse_extra_blank_lines()
maybe_run_ruff()

print("Done.")
print()
