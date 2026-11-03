from django.urls import path

from {{cookiecutter.project_slug}}.file_manager.apis.files import (
    ManagedFileDownloadApiView,
    ManagedFileListCreateApiView,
    ManagedFileRetrieveDestroyApiView,
)

app_name = "file_manager"

urlpatterns = [
    path("", ManagedFileListCreateApiView.as_view(), name="files-list-create"),
{%- if cookiecutter.use_uuid_pk == "y" %}
    path("<uuid:file_id>/", ManagedFileRetrieveDestroyApiView.as_view(), name="files-detail"),
    path("<uuid:file_id>/download/", ManagedFileDownloadApiView.as_view(), name="files-download"),
{%- else %}
    path("<int:file_id>/", ManagedFileRetrieveDestroyApiView.as_view(), name="files-detail"),
    path("<int:file_id>/download/", ManagedFileDownloadApiView.as_view(), name="files-download"),
{%- endif %}
]
