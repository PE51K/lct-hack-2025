"""Models for ETL generation requests and responses."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .common import ThreadUserIds
from .dag import DAG
from .ddl import DDL
from .extract import ExtractConfig
from .load import LoadConfig
from .transform import TransformConfig


class GenerateETLRequest(BaseModel):
    """Request from FastAPI to Callable/AI to generate ETL artefacts.

    Attributes:
        data_uri: User-provided connection string or pointer.
        ids: Correlation identifiers for audit and streaming.
    """

    data_uri: str = Field(..., description="Raw URI or connection string.")
    ids: ThreadUserIds


class GenerateETLResponse(BaseModel):
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
