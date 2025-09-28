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


class ExtractConfig(BaseModel):
    """
    Main extract config model.

    Attributes:
        source_metadata - section with tech source metadata
        content_metadata - list of content samples metadata (for every file, topic, etc.)
        content_statistics - content statistic section (any additional statistics about content)
    """

    source_metadata: Source | None = None
    content_metadata: list[Content] = Field(default_factory=list)
    content_statistics: dict | None = None
