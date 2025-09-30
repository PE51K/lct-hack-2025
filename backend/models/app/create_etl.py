"""Models for ETL creation requests and responses."""

from pydantic import BaseModel, Field

from ..dag import DAG
from ..ddl import DDL
from ..extract import ExtractConfig
from ..load import LoadConfig
from ..transform import TransformConfig
from .ids import ThreadUserIds


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
