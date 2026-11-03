import os
import shutil
from pathlib import Path

license_choice = "{{cookiecutter.license}}"
jwt = "{{cookiecutter.use_jwt}}"
sentry = "{{cookiecutter.use_sentry}}"
vscode = "{{cookiecutter.use_vscode}}"
code_style = "{{cookiecutter.use_code_style}}"
testing = "{{cookiecutter.use_testing}}"
celery = "{{cookiecutter.use_celery}}"
use_ci = "{{cookiecutter.use_ci}}"
ci_provider = "{{cookiecutter.ci_provider}}"
use_websockets = "{{cookiecutter.use_websockets}}"
use_pgadmin = "{{cookiecutter.use_pgadmin}}"
reverse_proxy = "{{cookiecutter.reverse_proxy}}"
project_slug = "{{cookiecutter.project_slug}}"


def delete_resource(resource):
    if os.path.isfile(resource):
        print(f"  - removed {resource}")
        os.remove(resource)
    elif os.path.isdir(resource):
        print(f"  - removed {resource}/")
        shutil.rmtree(resource)


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
if sentry == "n":
    delete_resource("config/settings/sentry.py")
    delete_resource(".cursor/rules/sentry.mdc")
if use_pgadmin != "y":
    delete_resource(".cursor/rules/pgadmin.mdc")
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

if use_ci != "y":
    delete_resource(".github")
    delete_resource(".gitlab-ci.yml")
elif ci_provider == "github":
    delete_resource(".gitlab-ci.yml")
elif ci_provider == "gitlab":
    delete_resource(".github")
else:
    # Unknown provider — drop both rather than leave the wrong one.
    delete_resource(".github")
    delete_resource(".gitlab-ci.yml")

print("Done.")
print()
