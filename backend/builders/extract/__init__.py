"""Extract configuration builders for various data sources."""

import sys
from typing import ClassVar

sys.path.insert(0, ".")

from models.extract import ExtractConfig, Source, SourceType

from .base import BaseExtractConfigBuilder
from .clickhouse import ClickHouseExtractConfigBuilder
from .folder import FolderExtractConfigBuilder
from .kafka import KafkaExtractConfigBuilder
from .postgres import PostgresExtractConfigBuilder
from .s3 import S3ExtractConfigBuilder


class ExtractConfigBuilder:
    """Builder class for creating ExtractConfig instances from URIs.

    This class recognizes source types from URI prefixes and delegates
    metadata extraction to specific builder classes.
    """

    source_to_builder_map: ClassVar[dict[SourceType, type[BaseExtractConfigBuilder]]] = {
        SourceType.folder: FolderExtractConfigBuilder,
        SourceType.kafka: KafkaExtractConfigBuilder,
        SourceType.PostgreSQL: PostgresExtractConfigBuilder,
        SourceType.ClickHouse: ClickHouseExtractConfigBuilder,
        SourceType.s3: S3ExtractConfigBuilder,
    }

    @staticmethod
    async def recognise_source(source: str) -> Source:
        """Recognize source type and extract connection string from URI.

        Parses URI prefixes to determine the source type and strips the prefix
        to get the connection string.

        Args:
            source: The input URI string.

        Returns:
            A Source object with type and connection string.
        """
        if "file:" in source:
            src = Source(
                source_type=SourceType.folder, connection_string=source.replace("file:", "")
            )
        elif "kafka:" in source:
            src = Source(
                source_type=SourceType.kafka, connection_string=source.replace("kafka:", "")
            )
        elif "postgres:" in source:
            src = Source(
                source_type=SourceType.PostgreSQL, connection_string=source.replace("postgres:", "")
            )
        elif "clickhouse:" in source:
            src = Source(
                source_type=SourceType.ClickHouse,
                connection_string=source.replace("clickhouse:", ""),
            )
        elif "s3:" in source:
            src = Source(source_type=SourceType.s3, connection_string=source.replace("s3:", ""))
        else:
            src = Source(source_type=SourceType.na, connection_string="")

        return src

    @classmethod
    async def from_uri(cls, uri: str) -> ExtractConfig:
        """Build an ExtractConfig from a URI.

        Recognizes the source type, then uses the appropriate builder to
        extract metadata, content type, and statistics.

        Args:
            uri: The source URI.

        Returns:
            A complete ExtractConfig object.
        """
        src = await cls.recognise_source(uri)

        src.content_type = await cls.source_to_builder_map[src.source_type].get_src_content_type(
            src
        )
        content_metadata = await cls.source_to_builder_map[src.source_type].get_content_metadata(
            src
        )
        content_statistics = await cls.source_to_builder_map[
            src.source_type
        ].get_content_statistics(src)

        return ExtractConfig(
            source_metadata=src,
            content_metadata=content_metadata,
            content_statistics=content_statistics,
        )
