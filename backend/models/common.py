"""Common models shared across the application."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ThreadUserIds(BaseModel):
    """Tuple of thread and user identifiers.

    Attributes:
        thread_id: Logical conversation or workflow run id.
        user_id: End-user id (can be a login, UUID, or email).
    """

    thread_id: str = Field(..., description="Conversation/workflow run id.")
    user_id: str = Field(..., description="End-user identity.")
