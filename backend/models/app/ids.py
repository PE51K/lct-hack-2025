"""Models for user and thread identifiers."""

from pydantic import BaseModel, Field


class ThreadUserIds(BaseModel):
    """User and thread identifiers."""

    user_id: str = Field(..., description="Unique identifier for the user.")
    thread_id: str = Field(..., description="Unique identifier for the thread.")
