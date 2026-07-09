from django.urls import include, path

urlpatterns = [
    path("", include(("{{cookiecutter.project_slug}}.core.urls", "core"))),
{%- if cookiecutter.use_jwt == "y" %}
    path("auth/", include(("{{cookiecutter.project_slug}}.authentication.urls", "authentication"))),
    path("users/", include(("{{cookiecutter.project_slug}}.users.urls", "users"))),
{%- endif %}
    # path("blog/", include(("{{cookiecutter.project_slug}}.blog.urls", "blog"))),
]
