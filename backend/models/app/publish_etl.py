"""Models for ETL publish requests and responses."""

from pydantic import BaseModel, Field

from .ids import ThreadUserIds


class PublishETLRequest(BaseModel):
    """ETL publish request."""

    ids: ThreadUserIds = Field(..., description="Unique identifiers for user and thread.")
    trigger_immediately: bool = Field(
        False, description="Whether to trigger DAG execution immediately after verification."
    )


class PublishETLResponse(BaseModel):
    """Streaming-friendly response summarizing publishing progress."""

    # Unique identifiers for user and thread
    ids: ThreadUserIds = Field(..., description="Unique identifiers for user and thread.")

    # Process tracking
    processing_done: bool = Field(False, description="Flag indicating if processing is complete.")
    processing_percentage_done: float = Field(
        ..., ge=0.0, le=100.0, description="Progress percentage from 0 to 100."
    )
    processing_message: str = Field(..., description="Current processing step message.")

    # Success flag
    success: bool = Field(..., description="Indicates if the ETL publishing was successful.")
    error_message: str | None = Field(None, description="Error message if the publishing failed.")

    # DAG information
    dag_id: str | None = Field(None, description="The DAG identifier in Airflow.")
    dag_status: str | None = Field(
        None, description="Status of the DAG (registered, triggered, etc.)."
    )
    dag_run_id: str | None = Field(None, description="The run ID if DAG was triggered.")
    airflow_url: str | None = Field(None, description="URL to view the DAG in Airflow UI.")
