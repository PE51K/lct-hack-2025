"""Models for data extraction configurations."""

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    """Enumeration of source types."""

    na = "na"
    folder = "folder"
    PostgreSQL = "PostgreSQL"
    ClickHouse = "ClickHouse"
    kafka = "kafka"
    s3 = "s3"


class ContentType(str, Enum):
    """Enumeration of content types."""

    na = "na"
    csv = "csv"
    xml = "xml"
    json = "json"
    table = "table"


class Source(BaseModel):
    """
    MetaData describe technological source itself.

    Attributes:
        source_type - tech type of source folder, kafka etc.
        connection_string - connection string to connect to source to get metadata.
        content_type - type of content in source csv json etc.
    """

    source_type: Annotated[str, SourceType] = SourceType.na
    connection_string: str
    content_type: Annotated[str, ContentType] | None = None


class Content(BaseModel):
    """
    Metadata fore single pice of source data. flat for flat source, nested for nested source.

    Attributes:
        message_name: file name, message offset from kafka, table name from db etc
        metamodel: metamodel of message in source in json schema format (https://json-schema.org/specification)
    """

    message_name: str
    metamodel: dict


class ExtractSchedule(BaseModel):
    """Scheduling configuration for data extraction."""
    
    interval: str = "@daily"  # Cron expression
    start_date: str = "2025-01-01"
    end_date: str | None = None
    catchup: bool = False
    max_active_runs: int = 1
    depends_on_past: bool = False


class ExtractResourceConfig(BaseModel):
    """Resource requirements for extraction."""
    
    cpu_request: float = 1.0
    memory_request_mb: int = 512
    disk_space_gb: int = 10
    timeout_minutes: int = 60
    retry_count: int = 3
    parallel_workers: int = 1


class IncrementalConfig(BaseModel):
    """Configuration for incremental data loading."""
    
    enabled: bool = False
    key_field: str | None = None
    lookback_days: int = 1
    checkpoint_enabled: bool = True


class DataQualityProfile(BaseModel):
    """Data quality metrics and thresholds."""
    
    completeness_threshold: float = 0.95
    accuracy_threshold: float = 0.98
    consistency_checks: list[str] = ["date_format", "data_types"]
    freshness_hours: int = 24
    volume_min_records: int = 1
    volume_max_records: int | None = None
    schema_validation: bool = True
    duplicate_detection: bool = True
    schema_drift_detection: bool = True
    duplicate_threshold: float = 0.05


class ExtractConfig(BaseModel):
    """
    Enhanced extract configuration model.

    Attributes:
        source_metadata - section with tech source metadata
        content_metadata - list of content samples metadata (for every file, topic, etc.)
        content_statistics - content statistic section (any additional statistics about content)
        schedule - scheduling configuration for extraction
        resources - resource requirements for extraction
        incremental - incremental loading configuration
        data_quality - data quality profile and validation rules
    """

    source_metadata: Source | None = None
    content_metadata: list[Content] = Field(default_factory=list)
    content_statistics: dict | None = None
    schedule: ExtractSchedule = Field(default_factory=ExtractSchedule)
    resources: ExtractResourceConfig = Field(default_factory=ExtractResourceConfig)
    incremental: IncrementalConfig = Field(default_factory=IncrementalConfig)
    data_quality: DataQualityProfile = Field(default_factory=DataQualityProfile)
