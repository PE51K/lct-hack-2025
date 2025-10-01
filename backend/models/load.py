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

    name: str
    data_type: str | None = None
    nullable: bool | None = None
    indexing_order: str | None = None


class Index(BaseModel):
    """Description for index for relational db table."""

    name: str
    is_clustered: bool
    fields: list[ColumnField]


class FlatMetaModel(BaseModel):
    """Metamodel for relational or columnstore db structured data."""

    fields: list[ColumnField]
    indexes: list[Index] | None = None
    partitioning_key: str


class NestingMetaModel(BaseModel):
    """Metamodel for nonstructured data."""

    data_structure: dict
    partitioning_key: str


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

    batch_size: int = 1000
    parallel_loads: int = 1
    commit_interval: int = 1000
    error_threshold: float = 0.05


class PartitioningConfig(BaseModel):
    """Partitioning configuration."""

    enabled: bool = False
    partition_by: str | None = None
    partition_type: PartitionType = PartitionType.DATE
    partition_count: int | None = None


class IndexingConfig(BaseModel):
    """Indexing configuration."""

    auto_index: bool = True
    custom_indexes: list[dict] = Field(default_factory=list)
    primary_key: list[str] = Field(default_factory=list)
    unique_constraints: list[list[str]] = Field(default_factory=list)


class CompressionConfig(BaseModel):
    """Compression configuration."""

    enabled: bool = True
    algorithm: CompressionAlgorithm = CompressionAlgorithm.GZIP
    level: int = 6


class LoadResourceConfig(BaseModel):
    """Resource configuration for loading."""

    cpu_request: float = 1.0
    memory_request_mb: int = 512
    disk_io_limit: str | None = None
    connection_pool_size: int = 10
    timeout_minutes: int = 30


class MonitoringConfig(BaseModel):
    """Monitoring configuration."""

    track_row_counts: bool = True
    track_execution_time: bool = True
    alert_on_failure: bool = True
    custom_metrics: list[str] = Field(default_factory=list)


class LoadConfig(BaseModel):
    """
    Enhanced load step configuration.

    Attributes:
        target_storage_type: Target storage system type (e.g., 'postgres', 'clickhouse', 'hdfs')
        target_storage_connection_string: target storage connection string
        nesting_metamodel: metamodel for hdfs
        flat_meta_model: metamodel for click and pg
        load_strategy: Strategy for loading data
        batch_config: Batch processing configuration
        partitioning: Partitioning configuration
        indexing: Indexing configuration
        compression: Compression configuration
        resources: Resource configuration
        monitoring: Monitoring configuration
    """

    target_storage_type: TargetStorageTypeRecommendation
    target_storage_connection_string: str
    nesting_metamodel: NestingMetaModel
    flat_meta_model: FlatMetaModel
    load_strategy: LoadStrategy = LoadStrategy.APPEND
    batch_config: BatchConfig = Field(default_factory=BatchConfig)
    partitioning: PartitioningConfig = Field(default_factory=PartitioningConfig)
    indexing: IndexingConfig = Field(default_factory=IndexingConfig)
    compression: CompressionConfig = Field(default_factory=CompressionConfig)
    resources: LoadResourceConfig = Field(default_factory=LoadResourceConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
