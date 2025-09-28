"""Models for updating ETL configurations based on user feedback."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .common import ThreadUserIds
from .dag import DAG
from .ddl import DDL
from .extract import ExtractConfig
from .load import LoadConfig
from .transform import TransformConfig


class FeedbackItem(BaseModel):
    """Single user feedback entry bound to a stage or artefact.

    Attributes:
        area: Target area: 'extract'|'load'|'transform'|'dag'.
        message: Free-text user comment about what is wrong.
        suggestion: Optional suggestion on how to fix.
    """

    area: str
    message: str
    suggestion: str | None = None


class Feedback(BaseModel):
    """Feedback message sent from GUI back to AI for refinement."""

    items: list[FeedbackItem] = Field(default_factory=list)
    overall: str | None = Field(None, description="General comment from user.")


class UpdateETLRequest(BaseModel):
    """Request from FastAPI to Callable/AI to update ETL artefacts based on feedback.

    Attributes:
        feedback: User-provided feedback on what to improve.
        ids: Correlation identifiers for audit and streaming.
    """

    feedback: Feedback
    ids: ThreadUserIds


class UpdateETLResponse(BaseModel):
    """
    Streaming-friendly response summarizing generated artefacts.

    Attributes:
        ids: Correlation identifiers for audit and streaming.
        message: Human-readable progress or summary.
        done: Whether the generation is complete.
        extract_config: Generated extract phase configuration.
        transform_config: Generated transform phase configuration.
        load_config: Generated load phase configuration.
        ddl: Generated DDL.
        dag: Generated DAG.
    """

    ids: ThreadUserIds
    message: str = Field(..., description="Human-readable progress or summary.")
    done: bool = False
    extract_config: ExtractConfig | None = Field(
        None, description="Generated extract phase configuration."
    )
    transform_config: TransformConfig | None = Field(
        None, description="Generated transform phase configuration."
    )
    load_config: LoadConfig | None = Field(None, description="Generated load phase configuration.")
    ddl: DDL | None = Field(None, description="Generated DDL.")
    dag: DAG | None = Field(None, description="Generated DAG.")
