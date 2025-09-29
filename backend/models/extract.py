"""Models for data extraction configurations."""

from enum import Enum

from pydantic import BaseModel

class PostgreSqlDataType(Enum):
    # Числовые типы
    SMALLINT = 'smallint'
    INTEGER = 'integer'
    BIGINT = 'bigint'
    DECIMAL = 'decimal'
    NUMERIC = 'numeric'
    REAL = 'real'
    DOUBLE_PRECISION = 'double precision'
    SMALLSERIAL = 'smallserial'
    SERIAL = 'serial'
    BIGSERIAL = 'bigserial'
    
    # Символьные типы
    CHARACTER_VARYING = 'character varying'
    VARCHAR = 'varchar'
    CHARACTER = 'character'
    CHAR = 'char'
    TEXT = 'text'
    
    # Бинарные типы
    BYTEA = 'bytea'
    
    # Дата/время
    TIMESTAMP = 'timestamp without time zone'
    TIMESTAMPTZ = 'timestamp with time zone'
    DATE = 'date'
    TIME = 'time without time zone'
    TIMETZ = 'time with time zone'
    INTERVAL = 'interval'
    
    # Логический тип
    BOOLEAN = 'boolean'
    BOOL = 'bool'
    
    # Перечисляемые типы
    ENUM = 'USER-DEFINED'  # В information_schema enum'ы отображаются как USER-DEFINED
    
    # Геометрические тимы
    POINT = 'point'
    LINE = 'line'
    LSEG = 'lseg'
    BOX = 'box'
    PATH = 'path'
    POLYGON = 'polygon'
    CIRCLE = 'circle'
    
    # Сетевые адреса
    INET = 'inet'
    CIDR = 'cidr'
    MACADDR = 'macaddr'
    MACADDR8 = 'macaddr8'
    
    # Bit строки
    BIT = 'bit'
    BIT_VARYING = 'bit varying'
    VARBIT = 'varbit'
    
    # Текстовые поисковые типы
    TSVECTOR = 'tsvector'
    TSQUERY = 'tsquery'
    
    # UUID
    UUID = 'uuid'
    
    # XML
    XML = 'xml'
    
    # JSON
    JSON = 'json'
    JSONB = 'jsonb'
    
    # Массивы
    ARRAY = 'ARRAY'  # Массивы в information_schema имеют суффикс []
    
    # Другие типы
    OID = 'oid'
    REGPROC = 'regproc'
    REGPROCEDURE = 'regprocedure'
    REGOPER = 'regoper'
    REGOPERATOR = 'regoperator'
    REGCLASS = 'regclass'
    REGTYPE = 'regtype'
    REGROLE = 'regrole'
    REGNAMESPACE = 'regnamespace'
    REGCONFIG = 'regconfig'
    REGDICTIONARY = 'regdictionary'

SourceType = Enum(
    "Source_type",
    [
        ("na", 1),
        ("folder", 2),
        ("PostgreSQL", 3),
        ("ClickHouse", 4),
        ("kafka", 5),
        ("hadoop", 6),
        ("sparkstreaming", 7),
        ("s3", 8),
    ],
)
ContentType = Enum(
    "Content_type",
    [
        ("na", 1),
        ("csv", 2),
        ("xml", 3),
        ("json", 4),
        ("table", 5),
        ("parquet", 6)
    ]
)

"""Tuple of thread and user identifiers.

Attributes:
    thread_id: Logical conversation or workflow run id.
    user_id: End-user id (can be a login, UUID, or email).
"""


class Source(BaseModel):
    """
    MetaData describe technological source itself.

    Attributes:
        source_type - tech type of source folder, kafka etc.
        connection_string - connection string to connect to source to get metadata.
        content_type - type of content in source csv json etc.
        table_name - name of table in db (optional, just for postgresql)
    """

    source_type: SourceType = SourceType.na
    connection_string: str | None = None
    content_type: ContentType | None = None
    table_name: str | None = None

class Attribute(BaseModel):
    """ 
    description for single atribute 

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
    data_type: PostgreSqlDataType
    is_nullable: bool
    character_maximum_length: int
    numeric_precision: int
    numeric_scale: int

class Content(BaseModel):
    """
    Metadata fore single pice of source data. flat for flat source, nested for nested source.

    Attributes:
        message_name: file name, topic from kafka, table name from db etc
        is_complex_nesting_present: is complex nesting present in message (we store messges with complex nesting in hdfs)
        metamodel: metamodel of message in source in json schema format (https://json-schema.org/specification)
    """

    message_name: str
    is_complex_nesting_present: bool = False
    metamodel: list[Attribute] | None = None


class ExtractConfig(BaseModel):
    """
    Main extract config model.

    Attributes:
        source_metadata - section with tech source metadata
        content_metadata - content metadat aggregated from all samples
        content_statistics - content statistic section (any additional statistics about content)
    """

    source_metadata: Source | None = None
    content_metadata: Content | None = None
    content_statistics: dict | None = None
