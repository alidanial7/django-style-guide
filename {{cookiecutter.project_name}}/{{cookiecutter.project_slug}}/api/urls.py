from django.urls import include, path

urlpatterns = [
    path("", include(("{{cookiecutter.project_slug}}.core.urls", "core"))),
    path("auth/", include(("{{cookiecutter.project_slug}}.users.urls.auth_url", "auth"))),
    path("users/", include(("{{cookiecutter.project_slug}}.users.urls.users_url", "users"))),
{%- if cookiecutter.use_file_manager == "y" %}
    path(
        "files/",
        include(("{{cookiecutter.project_slug}}.file_manager.urls.file_manager_url", "file_manager")),
    ),
{%- endif %}
{%- if cookiecutter.use_scoped_apis == "y" %}
    path("site/", include(("{{cookiecutter.project_slug}}.api.site_urls", "site"))),
{%- endif %}
    # path("blogs/", include(("{{cookiecutter.project_slug}}.blogs.urls.blogs_url", "blogs"))),
]
