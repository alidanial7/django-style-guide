from django.urls import include, path

urlpatterns = [
    path("", include(("{{cookiecutter.project_slug}}.core.urls", "core"))),
{%- if cookiecutter.use_jwt == "y" %}
    path("auth/", include(("{{cookiecutter.project_slug}}.users.urls.auth", "auth"))),
    path("users/", include(("{{cookiecutter.project_slug}}.users.urls.users", "users"))),
{%- endif %}
    # path("blogs/", include(("{{cookiecutter.project_slug}}.blogs.urls.blogs", "blogs"))),
]
