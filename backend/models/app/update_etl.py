"""Models for updating ETL update requests and responses."""

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from .ids import ThreadUserIds
from ..dag import DAG
from ..ddl import DDL
from ..extract import ExtractConfig
from ..load import LoadConfig
from ..transform import TransformConfig


class FeedbackAreaEnum(str, Enum):
    """Enumeration of feedback target areas."""

    EXTRACT = "extract"
    TRANSFORM = "transform"
    LOAD = "load"
    DDL = "ddl"
    DAG = "dag"


class FeedbackItem(BaseModel):
    """Single user feedback entry bound to a stage or artefact."""

    area: Annotated[str, FeedbackAreaEnum] = Field(..., description="Feedback area.")
    message: str = Field(..., description="Free-text user comment about what is wrong.")
    suggestion: str | None = Field(None, description="Optional suggestion on how to fix.")


class Feedback(BaseModel):
    """Feedback message sent from GUI back to AI for refinement."""

    items: list[FeedbackItem] = Field(default_factory=list, description="List of feedback items.")
    overall: str | None = Field(None, description="General comment from user.")


class UpdateETLRequest(BaseModel):
    """ETL update request."""

    # Unique identifiers for user and thread
    ids: ThreadUserIds = Field(..., description="Unique identifiers for user and thread.")

    # User feedback on what to improve
    feedback: Feedback = Field(..., description="User-provided feedback on what to improve.")

    # Artefacts to update
    extract_config: ExtractConfig = Field(..., description="Current extract phase configuration.")
    transform_config: TransformConfig = Field(..., description="Current transform phase configuration.")
    load_config: LoadConfig = Field(..., description="Current load phase configuration.")
    ddl: DDL = Field(..., description="Current DDL.")
    dag: DAG = Field(..., description="Current DAG.")


class UpdateETLResponse(BaseModel):
    """Streaming-friendly response summarizing updated artefacts."""

    # Unique identifiers for user and thread
    ids: ThreadUserIds = Field(..., description="Unique identifiers for user and thread.")

    # Process tracking
    processing_done: bool = Field(False, description="Flag indicating if processing is complete.")
    processing_percentage_done: float = Field(..., ge=0.0, le=100.0, description="Progress percentage from 0 to 100.")
    processing_message: str = Field(..., description="Current processing step message.")

    # Success flag
    success: bool = Field(..., description="Indicates if the ETL update was successful.")
    error_message: str | None = Field(None, description="Error message if the update failed.")

    # Updated artefacts
    extract_config: ExtractConfig | None = Field(
        None, description="Updated extract phase configuration."
    )
    transform_config: TransformConfig | None = Field(
        None, description="Updated transform phase configuration."
    )
    load_config: LoadConfig | None = Field(None, description="Updated load phase configuration.")
    ddl: DDL | None = Field(None, description="Updated DDL.")
    dag: DAG | None = Field(None, description="Updated DAG.")
