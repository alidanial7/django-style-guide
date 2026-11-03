from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import extend_schema_field, extend_schema_serializer
from rest_framework import serializers

from {{cookiecutter.project_slug}}.file_manager.enums import FileCategory
from {{cookiecutter.project_slug}}.file_manager.models import ManagedFile
from {{cookiecutter.project_slug}}.file_manager.validators import validate_managed_file


@extend_schema_serializer(
    component_name="ManagedFileOutput",
    description="Metadata payload for a managed file.",
)
class ManagedFileOutputSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = ManagedFile
        fields = [
            "id",
            "title",
            "original_filename",
            "file_size",
            "mime_type",
            "category",
            "is_public",
            "owner",
            "created_at",
            "updated_at",
            "download_url",
        ]
        read_only_fields = fields

    @extend_schema_field(serializers.URLField(help_text="Download URL for the managed file."))
    def get_download_url(self, obj: ManagedFile) -> str:
        try:
            from django.urls import reverse

            url = reverse("api:file_manager:files-download", kwargs={"file_id": obj.id})
        except Exception:
            url = f"/api/v1/files/{obj.id}/download/"

        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(url)
        return url


@extend_schema_serializer(
    component_name="ManagedFileInput",
    description="Input payload for uploading a new managed file.",
)
class ManagedFileInputSerializer(serializers.Serializer):
    file = serializers.FileField(
        required=True,
        help_text="Binary file to upload.",
    )
    title = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default="",
        help_text="Optional custom title for the file.",
    )
    category = serializers.ChoiceField(
        choices=FileCategory.choices,
        default=FileCategory.OTHER,
        help_text="File category (controls size/extension defaults and publicity).",
    )
    is_public = serializers.BooleanField(
        required=False,
        allow_null=True,
        default=None,
        help_text="If omitted/null, defaults from the category rule.",
    )

    def to_internal_value(self, data):
        if hasattr(data, "copy"):
            data = data.copy()
        elif isinstance(data, dict):
            data = data.copy()
        if data.get("is_public") == "":
            data["is_public"] = None
        return super().to_internal_value(data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        file = attrs.get("file")
        category = attrs.get("category", FileCategory.OTHER)
        if file:
            try:
                validate_managed_file(file, category=category)
            except DjangoValidationError as exc:
                raise serializers.ValidationError({"file": exc.messages})
        return attrs
