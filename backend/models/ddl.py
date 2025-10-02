"""Data Definition Language models."""

from pydantic import BaseModel, Field


class DDL(BaseModel):
    """Represents DDL statements."""

    statements: str = Field(..., description="DDL statements as a string")
