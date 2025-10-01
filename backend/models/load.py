"""Models for data loading configurations."""

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


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


class ColumnField(BaseModel):
    """Description for field in table."""

    name: str = Field(..., description="Name of the field.")
    data_type: str | None = Field(
        None, description="Data type of the field.", examples=["VARCHAR(255)", "INT", "DATE"]
    )
    nullable: bool | None = Field(None, description="Whether the field is nullable.")
    indexing_order: str | None = Field(None, description="Indexing order for the field.")


class Index(BaseModel):
    """Description for index for relational db table."""

    name: str = Field(..., description="Name of the index.")
    is_clustered: bool = Field(..., description="Whether the index is clustered.")
    fields: list[ColumnField] = Field(..., description="Fields included in the index.")


class FlatMetaModel(BaseModel):
    """Metamodel for relational or columnstore db structured data."""

    fields: list[ColumnField] = Field(..., description="List of fields in the model.")
    indexes: list[Index] | None = Field(None, description="List of indexes.")
    partitioning_key: str = Field(..., description="Key for partitioning.")


class NestingMetaModel(BaseModel):
    """Metamodel for nonstructured data."""

    data_structure: dict = Field(..., description="Data structure definition.")
    partitioning_key: str = Field(..., description="Key for partitioning.")


class LoadStrategy(str, Enum):
    """Data loading strategies."""

    APPEND = "append"
    UPSERT = "upsert"
    FULL_REFRESH = "full_refresh"
    INCREMENTAL = "incremental"
    MERGE = "merge"


class PartitionType(str, Enum):
    """Partitioning strategies."""

    DATE = "date"
    HASH = "hash"
    RANGE = "range"
    LIST = "list"


class CompressionAlgorithm(str, Enum):
    """Compression algorithms."""

    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"
    SNAPPY = "snappy"


class BatchConfig(BaseModel):
    """Batch loading configuration."""

    batch_size: int = Field(1000, description="Size of each batch.")
    parallel_loads: int = Field(1, description="Number of parallel loads.")
    commit_interval: int = Field(1000, description="Interval for commits.")
    error_threshold: float = Field(0.05, description="Threshold for errors.")


class PartitioningConfig(BaseModel):
    """Partitioning configuration."""

    enabled: bool = Field(False, description="Whether partitioning is enabled.")
    partition_by: str | None = Field(None, description="Field to partition by.")
    partition_type: Annotated[str, PartitionType] = Field(
        PartitionType.DATE, description="Type of partitioning."
    )
    partition_count: int | None = Field(None, description="Number of partitions.")


class IndexingConfig(BaseModel):
    """Indexing configuration."""

    auto_index: bool = True
    custom_indexes: list[dict] = Field(default_factory=list)
    primary_key: list[str] = Field(default_factory=list)
    unique_constraints: list[list[str]] = Field(default_factory=list)


class CompressionConfig(BaseModel):
    """Compression configuration."""

    enabled: bool = Field(True, description="Whether compression is enabled.")
    algorithm: Annotated[str, CompressionAlgorithm] = Field(
        CompressionAlgorithm.GZIP, description="Compression algorithm."
    )
    level: int = Field(6, description="Compression level.")


class LoadResourceConfig(BaseModel):
    """Resource configuration for loading."""

    cpu_request: float = Field(1.0, description="CPU request.")
    memory_request_mb: int = Field(512, description="Memory request in MB.")
    disk_io_limit: str | None = Field(None, description="Disk I/O limit.")
    connection_pool_size: int = Field(10, description="Connection pool size.")
    timeout_minutes: int = Field(30, description="Timeout in minutes.")


class MonitoringConfig(BaseModel):
    """Monitoring configuration."""

    track_row_counts: bool = True
    track_execution_time: bool = True
    alert_on_failure: bool = True
    custom_metrics: list[str] = Field(default_factory=list)


class LoadConfig(BaseModel):
    """Enhanced load step configuration."""

    target_storage_type: TargetStorageTypeRecommendation = Field(
        ..., description="Target storage system type."
    )
    target_storage_connection_string: str = Field(
        ..., description="Target storage connection string."
    )
    nesting_metamodel: NestingMetaModel = Field(..., description="Metamodel for hdfs.")
    flat_meta_model: FlatMetaModel = Field(..., description="Metamodel for click and pg.")
    load_strategy: Annotated[str, LoadStrategy] = Field(
        LoadStrategy.APPEND, description="Strategy for loading data."
    )
    batch_config: BatchConfig = Field(
        default_factory=BatchConfig, description="Batch processing configuration."
    )
    partitioning: PartitioningConfig = Field(
        default_factory=PartitioningConfig, description="Partitioning configuration."
    )
    indexing: IndexingConfig = Field(
        default_factory=IndexingConfig, description="Indexing configuration."
    )
    compression: CompressionConfig = Field(
        default_factory=CompressionConfig, description="Compression configuration."
    )
    resources: LoadResourceConfig = Field(
        default_factory=LoadResourceConfig, description="Resource configuration."
    )
    monitoring: MonitoringConfig = Field(
        default_factory=MonitoringConfig, description="Monitoring configuration."
    )
