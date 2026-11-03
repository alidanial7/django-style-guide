from drf_spectacular.utils import extend_schema
from rest_framework import parsers, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from {{cookiecutter.project_slug}}.api.mixins import ApiAuthMixin
from {{cookiecutter.project_slug}}.api.pagination import LimitOffsetPagination, get_paginated_response_context
from {{cookiecutter.project_slug}}.common.http import api_response
from {{cookiecutter.project_slug}}.common.http.schema import envelope_serializer
from {{cookiecutter.project_slug}}.file_manager.apis.files.files_serializers import (
    ManagedFileInputSerializer,
    ManagedFileOutputSerializer,
)
from {{cookiecutter.project_slug}}.file_manager.constants import FILE_MANAGER_TAGS
from {{cookiecutter.project_slug}}.file_manager.selectors import (
    get_managed_file,
    list_managed_files_for_user,
    user_can_access_managed_file,
)
from {{cookiecutter.project_slug}}.file_manager.services import (
    create_managed_file,
    delete_managed_file,
    serve_managed_file_securely,
)


class ManagedFileListCreateApiView(ApiAuthMixin, APIView):
    """List files owned by the current user and upload new files."""

    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    Pagination = LimitOffsetPagination

    @extend_schema(
        tags=FILE_MANAGER_TAGS,
        operation_id="files_list",
        summary="List owned managed files",
        responses=ManagedFileOutputSerializer(many=True),
    )
    def get(self, request):
        qs = list_managed_files_for_user(user=request.user)
        return get_paginated_response_context(
            pagination_class=self.Pagination,
            serializer_class=ManagedFileOutputSerializer,
            queryset=qs,
            request=request,
            view=self,
        )

    @extend_schema(
        tags=FILE_MANAGER_TAGS,
        operation_id="files_create",
        summary="Upload a new managed file",
        request=ManagedFileInputSerializer,
        responses={201: envelope_serializer("ManagedFileCreateEnvelope", ManagedFileOutputSerializer)},
    )
    def post(self, request):
        serializer = ManagedFileInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        managed_file = create_managed_file(
            user=request.user,
            data=serializer.validated_data,
        )

        return api_response(
            data=ManagedFileOutputSerializer(managed_file, context={"request": request}).data,
            http_status=status.HTTP_201_CREATED,
        )


class ManagedFileRetrieveDestroyApiView(ApiAuthMixin, APIView):
    """Retrieve metadata or delete a managed file."""

    @extend_schema(
        tags=FILE_MANAGER_TAGS,
        operation_id="files_retrieve",
        summary="Retrieve managed file metadata",
        responses=envelope_serializer("ManagedFileDetailEnvelope", ManagedFileOutputSerializer),
    )
    def get(self, request, file_id, **kwargs):
        file_obj = get_managed_file(file_id=file_id)
        if not file_obj:
            raise NotFound("managed file not found.")
        if not user_can_access_managed_file(user=request.user, managed_file=file_obj):
            raise PermissionDenied("file access denied.")
        return api_response(
            data=ManagedFileOutputSerializer(file_obj, context={"request": request}).data,
            http_status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=FILE_MANAGER_TAGS,
        operation_id="files_delete",
        summary="Delete a managed file",
        responses={204: None},
    )
    def delete(self, request, file_id, **kwargs):
        file_obj = get_managed_file(file_id=file_id)
        if not file_obj:
            raise NotFound("managed file not found.")
        if not user_can_access_managed_file(user=request.user, managed_file=file_obj, write=True):
            raise PermissionDenied("file access denied.")
        delete_managed_file(managed_file=file_obj)
        return api_response(http_status=status.HTTP_204_NO_CONTENT)


class ManagedFileDownloadApiView(APIView):
    """Stream binary file content (public files allowed without auth)."""

    authentication_classes = ApiAuthMixin.authentication_classes
    permission_classes = [AllowAny]

    @extend_schema(
        tags=FILE_MANAGER_TAGS,
        operation_id="files_download",
        summary="Download or stream binary file content",
        responses={200: bytes},
    )
    def get(self, request, file_id, **kwargs):
        file_obj = get_managed_file(file_id=file_id)
        if not file_obj:
            raise NotFound("managed file not found.")
        if not user_can_access_managed_file(user=request.user, managed_file=file_obj):
            raise PermissionDenied("file access denied.")
        return serve_managed_file_securely(managed_file=file_obj)
