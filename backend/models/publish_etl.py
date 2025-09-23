"""Models for publisher reports."""

from __future__ import annotations

from pydantic import BaseModel

from .common import ThreadUserIds


class PublishETLRequest(BaseModel):
    """Request from FastAPI to publish ETL artefacts."""

    ids: ThreadUserIds


class PublishETLResponse(BaseModel):
    """
    Streaming-friendly response summarizing publishing progress.

    Attributes:
        ids: Correlation identifiers for audit and streaming.
        message: Human-readable progress or summary.
        done: Whether the publishing is complete.
        success: Whether the publishing was successful.
    """

    ids: ThreadUserIds
    message: str
    done: bool = False
    success: bool = False
