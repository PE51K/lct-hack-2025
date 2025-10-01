"""Models for data extraction configurations."""

from enum import Enum

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
    """
    Metadata describing the technological source itself.

    Attributes:
        source_type - tech type of source folder, kafka etc.
        connection_string - connection string to connect to source to get metadata.
        table_name - name of table in db (optional, just for postgresql)
    """

    source_type: SourceType = SourceType.na
    connection_string: str | None = None
    table_name: str | None = None


class Attribute(BaseModel):
    """
    Description for single attribute.

    Attributes:
        order_no: order of attribute in metamodel
        column_name: name of column in source
        data_type: type of column in source
        is_nullable: is column nullable
        character_maximum_length: max length of string column
        numeric_precision: max precision of numeric column
        numeric_scale: scale of numeric column

    Example of metamodel:

    json:
    {
        "number":1,
        "order_name":"order",
        "item":{
            "item_no":1,
            "item_name":"item",
            "item_details":"details"
        }
    }

    metamodel for this json
    [
        {
            "order_no": 1,
            "column_name": "number",
            "data_type": "integer",
            "is_nullable": false,
            "character_maximum_length": null,
            "numeric_precision": 10,
            "numeric_scale": 0
        },
        {
            "order_no": 2,
            "column_name": "order_name",
            "data_type": "character varying",
            "is_nullable": false,
            "character_maximum_length": 255,
            "numeric_precision": null,
            "numeric_scale": null
        },
        {
            "order_no": 3,
            "column_name": "item.item_no",
            "data_type": "integer",
            "is_nullable": false,
            "character_maximum_length": null,
            "numeric_precision": 10,
            "numeric_scale": 0
        },
        {
            "order_no": 4,
            "column_name": "item.item_name",
            "data_type": "character varying",
            "is_nullable": false,
            "character_maximum_length": 255,
            "numeric_precision": null,
            "numeric_scale": null
        },
        {
            "order_no": 5,
            "column_name": "item.item_details",
            "data_type": "character varying",
            "is_nullable": true,
            "character_maximum_length": 255,
            "numeric_precision": null,
            "numeric_scale": null
        }
    ]
    """

    order_no: int
    column_name: str
    data_type: str | None = None
    is_nullable: bool
    character_maximum_length: int | None = None
    numeric_precision: int | None = None
    numeric_scale: int | None = None


class Content(BaseModel):
    """
    Metadata for single piece of source data. Flat for flat source, nested for nested source.

    Attributes:
        message_name: file name, topic from kafka, table name from db etc
        is_complex_nesting_present: is complex nesting present in message
            (we store messages with complex nesting in hdfs)
        metamodel: metamodel of message (see Attribute model and example above)
    """

    message_name: str
    is_complex_nesting_present: bool = False
    metamodel: list[Attribute] | None = None


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
        content_metadata - content metadat aggregated from all samples
        content_statistics - content statistic section (any additional statistics about content)
        schedule - scheduling configuration for extraction
        resources - resource requirements for extraction
        incremental - incremental loading configuration
        data_quality - data quality profile and validation rules
        content_type - type of content in source csv json etc.
    """

    source_metadata: Source | None = None
    content_metadata: Content | None = None
    content_statistics: dict | None = None
    schedule: ExtractSchedule = Field(default_factory=ExtractSchedule)
    resources: ExtractResourceConfig = Field(default_factory=ExtractResourceConfig)
    incremental: IncrementalConfig = Field(default_factory=IncrementalConfig)
    data_quality: DataQualityProfile = Field(default_factory=DataQualityProfile)
    content_type: ContentType | None = None
