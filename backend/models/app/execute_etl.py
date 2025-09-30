"""Models for ETL execution requests and responses."""

from pydantic import BaseModel, Field

from .ids import ThreadUserIds


class ExecuteETLRequest(BaseModel):
    """ETL execution request."""

    ids: ThreadUserIds = Field(..., description="Unique identifiers for user and thread.")


class ExecuteETLResponse(BaseModel):
    """Streaming-friendly response for ETL execution."""

    ids: ThreadUserIds = Field(..., description="Unique identifiers for user and thread.")

    message: str = Field(..., description="Current execution message.")
    done: bool = Field(False, description="Flag indicating if execution is complete.")
    success: bool = Field(False, description="Indicates if the execution was successful.")
