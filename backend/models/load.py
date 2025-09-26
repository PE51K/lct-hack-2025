"""Models for data loading configurations."""

from __future__ import annotations

from enum import Enum
from typing import Annotated

from pydantic import BaseModel


class TargetStorageEnum(str, Enum):
    """Enumeration of supported target storage types for data loading."""

    POSTGRES = "postgres"
    CLICKHOUSE = "clickhouse"
    HDFS = "hdfs"


class TargetStorageTypeRecommendation(BaseModel):
    """
    Target storage type recommendation from AI.

    Attributes:
        storage_type: Target storage system type (e.g., 'postgres', 'clickhouse', 'hdfs').
        explanation: Human-readable explanation of the recommendation.
    """

    storage_type: Annotated[str, TargetStorageEnum]
    explanation: str


class LoadConfig(BaseModel):
    """
    Load step configuration.

    Attributes:
        target_storage_type: Target storage system type (e.g., 'postgres', 'clickhouse
    """

    target_storage_type: TargetStorageTypeRecommendation
    # TODO: Complete this model
