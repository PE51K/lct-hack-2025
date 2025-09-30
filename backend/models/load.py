"""Models for data loading configurations."""

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


class Field(BaseModel):
    """Description for field in table."""

    name: str
    data_type: str | None = None
    nullable: bool | None = None
    indexing_order: str | None = None


class Index(BaseModel):
    """Description for index for relational db table."""

    name: str
    is_clustered: bool
    fields: list[Field]


class FlatMetaModel(BaseModel):
    """Metamodel for relational or columnstore db structured data."""

    fields: list[Field]
    indexes: list[Index] | None = None
    partitioning_key: str


class NestingMetaModel(BaseModel):
    """Metamodel for nonstructured data."""

    data_structure: dict
    partitioning_key: str


class LoadConfig(BaseModel):
    """
    Load step configuration.

    Attributes:
        target_storage_type: Target storage system type (e.g., 'postgres', 'clickhouse', 'hdfs')
        target_storage_connection_string: target storage connection string
        nesting_model: metamodel for hdfs
        flat_meta_model: metamodel for click and pg
        index
        p
    """

    target_storage_type: TargetStorageTypeRecommendation
    target_storage_connection_string: str
    nesting_metamodel: NestingMetaModel
    flat_meta_model: FlatMetaModel
