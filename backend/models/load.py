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


class LoadConfig(BaseModel):
    """
    Load step configuration.

    Attributes:
        target_storage_type: Target storage system type (e.g., 'postgres', 'clickhouse
    """

    target_storage_type: Annotated[str, TargetStorageEnum]
    # TODO: Complete this model
