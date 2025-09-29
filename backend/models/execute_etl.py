"""Models for ETL execution requests and responses."""

from pydantic import BaseModel

from models.common import ThreadUserIds


class ExecuteETLRequest(BaseModel):
    """Request from FastAPI to execute ETL artefacts."""

    ids: ThreadUserIds


class ExecuteETLResponse(BaseModel):
    """
    Streaming-friendly response summarizing execution progress.

    Attributes:
        ids: Correlation identifiers for audit and streaming.
        message: Human-readable progress or summary.
        done: Whether the execution is complete.
        success: Whether the execution was successful.
    """

    ids: ThreadUserIds
    message: str
    done: bool = False
    success: bool = False
