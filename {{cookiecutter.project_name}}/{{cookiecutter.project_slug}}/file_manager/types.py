"""App-level TypedDicts for file_manager service inputs.

Define Create*/Update* TypedDicts here. Serializers validate HTTP; services take data: SomeData.
"""

from typing import NotRequired, TypedDict

from django.core.files.uploadedfile import UploadedFile


class CreateManagedFileData(TypedDict):
    file: UploadedFile
    title: NotRequired[str | None]
    category: NotRequired[str]
    is_public: NotRequired[bool | None]
