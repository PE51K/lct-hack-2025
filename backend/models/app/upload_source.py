"""Models for file upload processing."""

from pydantic import BaseModel, Field

from ..extract import ExtractConfig, ContentType
from .ids import ThreadUserIds


class UploadSourceResponse(BaseModel):
    """Response returned after processing an uploaded source file."""

    ids: ThreadUserIds = Field(..., description="Identifiers related to the upload.")
    filename: str = Field(..., description="Original filename of the uploaded source.")
    stored_path: str = Field(..., description="Absolute path of the stored file on the server.")
    source_uri: str = Field(..., description="URI pointing to the stored folder for further use.")
    container_source_uri: str = Field(
        ..., description="Container-accessible URI for Airflow runtime."
    )
    content_type: ContentType | None = Field(
        default=None, description="Detected content type for the uploaded source."
    )
    extract_config: ExtractConfig | None = Field(
        default=None,
        description="Extract configuration generated from the uploaded content.",
    )
