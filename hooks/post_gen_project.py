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
    delete_resource("config/settings/jwt.py")
else:
    delete_resource(f"{project_slug}/users/apis/auth/auth_session_apis.py")
if sentry == "n":
    delete_resource("config/settings/sentry.py")
if vscode == "n":
    delete_resource(".vscode")
if code_style == "n":
    delete_resource("pyproject.toml")
    delete_resource(".pre-commit-config.yaml")
    delete_resource(".flake8")
else:
    delete_resource("setup.cfg")
if celery == "n":
    delete_resource("config/celery.py")
    delete_resource("config/tasks.py")
    delete_resource("config/settings/celery.py")
    delete_resource("docker/celery_entrypoint.sh")
    delete_resource("docker/beats_entrypoint.sh")
if use_websockets != "y":
    delete_resource("config/settings/channels.py")
    delete_resource(f"{project_slug}/core/routing.py")
if reverse_proxy != "nginx":
    delete_resource("docker/nginx")
if reverse_proxy != "traefik":
    delete_resource("docker/traefik")
if testing == "n":
    delete_resource("pytest.ini")
    delete_resource("config/django/test.py")
    delete_resource(f"{project_slug}/conftest.py")
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
