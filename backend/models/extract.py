"""Models for data extraction configurations."""

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class PostgreSqlDataType(Enum):
    """PostgreSQL data types enumeration."""

    # Numeric types
    SMALLINT = "smallint"
    INTEGER = "integer"
    BIGINT = "bigint"
    DECIMAL = "decimal"
    NUMERIC = "numeric"
    REAL = "real"
    DOUBLE_PRECISION = "double precision"
    SMALLSERIAL = "smallserial"
    SERIAL = "serial"
    BIGSERIAL = "bigserial"

    # Character types
    CHARACTER_VARYING = "character varying"
    VARCHAR = "varchar"
    CHARACTER = "character"
    CHAR = "char"
    TEXT = "text"

    # Binary types
    BYTEA = "bytea"

    # Date/time
    TIMESTAMP = "timestamp without time zone"
    TIMESTAMPTZ = "timestamp with time zone"
    DATE = "date"
    TIME = "time without time zone"
    TIMETZ = "time with time zone"
    INTERVAL = "interval"

    # Logical type
    BOOLEAN = "boolean"
    BOOL = "bool"

    # Enumerated types
    ENUM = "USER-DEFINED"  # In information_schema enums are displayed as USER-DEFINED

    # Geometric types
    POINT = "point"
    LINE = "line"
    LSEG = "lseg"
    BOX = "box"
    PATH = "path"
    POLYGON = "polygon"
    CIRCLE = "circle"

    # Network addresses
    INET = "inet"
    CIDR = "cidr"
    MACADDR = "macaddr"
    MACADDR8 = "macaddr8"

    # Bit strings
    BIT = "bit"
    BIT_VARYING = "bit varying"
    VARBIT = "varbit"

    # Text search types
    TSVECTOR = "tsvector"
    TSQUERY = "tsquery"

    # UUID
    UUID = "uuid"

    # XML
    XML = "xml"

    # JSON
    JSON = "json"
    JSONB = "jsonb"

    # Arrays
    ARRAY = "ARRAY"  # Arrays in information_schema have suffix []

    # Other types
    OID = "oid"
    REGPROC = "regproc"
    REGPROCEDURE = "regprocedure"
    REGOPER = "regoper"
    REGOPERATOR = "regoperator"
    REGCLASS = "regclass"
    REGTYPE = "regtype"
    REGROLE = "regrole"
    REGNAMESPACE = "regnamespace"
    REGCONFIG = "regconfig"
    REGDICTIONARY = "regdictionary"


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
    """Metadata describing the technological source itself."""

    source_type: Annotated[str, SourceType] = Field(
        SourceType.na, description="Tech type of source folder, kafka etc."
    )
    connection_string: str | None = Field(
        None, description="Connection string to connect to source to get metadata."
    )
    table_name: str | None = Field(
        None, description="Name of table in db (optional, just for postgresql)."
    )
    bucket_name: str | None = Field(
        None, description="Bucket name for S3 sources (optional, just for S3)."
    )
    access_key: str | None = Field(
        None, description="Access key for S3 sources (optional, just for S3)."
    )
    secret_key: str | None = Field(
        None, description="Secret key for S3 sources (optional, just for S3)."
    )


class Attribute(BaseModel):
    """Description for single attribute."""

    order_no: int = Field(..., description="Order of attribute in metamodel.")
    column_name: str = Field(..., description="Name of column in source.")
    data_type: str | None = Field(None, description="Type of column in source.")
    is_nullable: bool = Field(..., description="Is column nullable.")
    character_maximum_length: int | None = Field(None, description="Max length of string column.")
    numeric_precision: int | None = Field(None, description="Max precision of numeric column.")
    numeric_scale: int | None = Field(None, description="Scale of numeric column.")


class Content(BaseModel):
    """Metadata for single piece of source data."""

    message_name: str = Field(
        ..., description="File name, topic from kafka, table name from db etc."
    )
    is_complex_nesting_present: bool = Field(
        False, description="Is complex nesting present in message."
    )
    content_type: Annotated[str, ContentType] | None = Field(
        None, description="Type of content in source."
    )
    metamodel: list[Attribute] | None = Field(None, description="Metamodel of message.")


class ExtractSchedule(BaseModel):
    """Scheduling configuration for data extraction."""

    interval: str = Field("@daily", description="Cron expression.")
    start_date: str = Field("2025-01-01", description="Start date for scheduling.")
    end_date: str | None = Field(None, description="End date for scheduling.")
    catchup: bool = Field(False, description="Whether to catch up on missed runs.")
    max_active_runs: int = Field(1, description="Maximum number of active runs.")
    depends_on_past: bool = Field(False, description="Whether task depends on past runs.")


class ExtractResourceConfig(BaseModel):
    """Resource requirements for extraction."""

    cpu_request: float = Field(1.0, description="CPU request for the task.")
    memory_request_mb: int = Field(512, description="Memory request in MB.")
    disk_space_gb: int = Field(10, description="Disk space in GB.")
    timeout_minutes: int = Field(60, description="Timeout in minutes.")
    retry_count: int = Field(3, description="Number of retries.")
    parallel_workers: int = Field(1, description="Number of parallel workers.")


class IncrementalConfig(BaseModel):
    """Configuration for incremental data loading."""

    enabled: bool = Field(False, description="Whether incremental loading is enabled.")
    key_field: str | None = Field(None, description="Field used as key for incremental loading.")
    lookback_days: int = Field(1, description="Number of days to look back.")
    checkpoint_enabled: bool = Field(True, description="Whether checkpointing is enabled.")


class DataQualityProfile(BaseModel):
    """Data quality metrics and thresholds."""

    completeness_threshold: float = Field(0.95, description="Threshold for data completeness.")
    accuracy_threshold: float = Field(0.98, description="Threshold for data accuracy.")
    consistency_checks: list[str] = Field(
        ["date_format", "data_types"], description="List of consistency checks."
    )
    freshness_hours: int = Field(24, description="Freshness requirement in hours.")
    volume_min_records: int = Field(1, description="Minimum number of records.")
    volume_max_records: int | None = Field(None, description="Maximum number of records.")
    schema_validation: bool = Field(True, description="Whether schema validation is enabled.")
    duplicate_detection: bool = Field(True, description="Whether duplicate detection is enabled.")
    schema_drift_detection: bool = Field(
        True, description="Whether schema drift detection is enabled."
    )
    duplicate_threshold: float = Field(0.05, description="Threshold for duplicate detection.")


class ExtractConfig(BaseModel):
    """Enhanced extract configuration model."""

    source_metadata: Source | None = Field(None, description="Section with tech source metadata.")
    content_metadata: list[Content] | None = Field(
        None, description="Content metadata aggregated from all samples."
    )
    content_statistics: dict | None = Field(None, description="Content statistic section.")
    schedule: ExtractSchedule = Field(
        default_factory=ExtractSchedule, description="Scheduling configuration for extraction."
    )
    resources: ExtractResourceConfig = Field(
        default_factory=ExtractResourceConfig, description="Resource requirements for extraction."
    )
    incremental: IncrementalConfig = Field(
        default_factory=IncrementalConfig, description="Incremental loading configuration."
    )
    data_quality: DataQualityProfile = Field(
        default_factory=DataQualityProfile, description="Data quality profile and validation rules."
    )
    batch_size: int = Field(1000, description="Batch size for processing records.")
