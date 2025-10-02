"""Models for ETL creation requests and responses."""

from typing import Any

from pydantic import BaseModel, Field

from ..dag import DAG
from ..ddl import DDL
from ..extract import ExtractConfig
from ..load import LoadConfig
from ..transform import TransformConfig
from .ids import ThreadUserIds


class CredentialField(BaseModel):
    """Field definition for credentials form."""

    name: str = Field(..., description="Field name")
    label: str = Field(..., description="Display label")
    type: str = Field(..., description="Input type: text, password, number")
    placeholder: str | None = Field(None, description="Placeholder text")
    default: Any | None = Field(None, description="Default value")
    required: bool = Field(True, description="Whether field is required")


class CredentialsRequired(BaseModel):
    """Credentials requirement specification."""

    target_type: str = Field(..., description="Target database type")
    fields: list[CredentialField] = Field(..., description="Required credential fields")


class CreateETLRequest(BaseModel):
    """ETL creation request."""

    ids: ThreadUserIds = Field(..., description="Unique identifiers for user and thread.")
    user_prompt: str = Field(
        ..., description="User's natural language prompt with connection string and requirements."
    )


class CreateETLResponse(BaseModel):
    """Streaming-friendly response summarizing created artefacts."""

    # Unique identifiers for user and thread
    ids: ThreadUserIds = Field(..., description="Unique identifiers for user and thread.")

    # Process tracking
    processing_done: bool = Field(False, description="Flag indicating if processing is complete.")
    processing_percentage_done: float = Field(
        ..., ge=0.0, le=100.0, description="Progress percentage from 0 to 100."
    )
    processing_message: str = Field(..., description="Current processing step message.")

    # Success flag
    success: bool = Field(..., description="Indicates if the ETL creation was successful.")
    error_message: str | None = Field(None, description="Error message if the creation failed.")

    # Created artefacts
    extract_config: ExtractConfig | None = Field(
        None, description="Created extract phase configuration."
    )
    transform_config: TransformConfig | None = Field(
        None, description="Created transform phase configuration."
    )
    load_config: LoadConfig | None = Field(None, description="Created load phase configuration.")
    ddl: DDL | None = Field(None, description="Created DDL.")
    dag: DAG | None = Field(None, description="Created DAG.")

    # NEW: Credentials form and next step
    credentials_required: CredentialsRequired | None = Field(
        None, description="Credentials form specification for target database."
    )
    next_step: str | None = Field(None, description="Next endpoint to call (e.g., 'create_dag').")
