"""Models for data extraction configurations."""

from __future__ import annotations

from enum import Enum
from typing import Annotated

from pydantic import BaseModel


class SourceTypeEnum(str, Enum):
    """Enumeration of supported source types for data extraction."""

    POSTGRES = "postgres"
    CLICKHOUSE = "clickhouse"
    KAFKA = "kafka"
    S3 = "s3"


class ExtractConfig(BaseModel):
    """
    Extract step configuration.

    Attributes:
        type: Source system type (e.g., 'postgres', 'clickhouse', 'kafka', 's3').
    """

    type: Annotated[str, SourceTypeEnum]
    # TODO: Complete this model
