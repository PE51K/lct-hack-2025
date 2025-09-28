"""Models for data extraction configurations."""

from enum import Enum

from pydantic import BaseModel, Field

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
    "Content_type", [("na", 1), ("csv", 2), ("xml", 3), ("json", 4), ("table", 5), ("parquet", 6)]
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
    """

    source_type: SourceType = SourceType.na
    connection_string: str
    content_type: ContentType | None = None


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
