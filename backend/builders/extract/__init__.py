"""Extract configuration builders for various data sources."""

import sys
from abc import ABC, abstractmethod
from typing import ClassVar

sys.path.insert(0, ".")

from models.extract import Content, ContentType, ExtractConfig, Source, SourceType

from .clickhouse import ClickHouseExtractConfigBuilder
from .csv import CsvExtractConfigBuilder
from .folder import FolderExtractConfigBuilder
from .hadoop import HadoopExtractConfigBuilder
from .kafka import KafkaExtractConfigBuilder
from .postgres import PostgresExtractConfigBuilder
from .s3 import S3ExtractConfigBuilder
from .sparkstreaming import SparkStreamingExtractConfigBuilder


class BaseExtractConfigBuilder(ABC):
    """
    Abstract base class for extract config builders.

    Subclasses must implement methods to extract metadata, content type, and statistics
    from various data sources.
    """

    @abstractmethod
    @classmethod
    async def get_content_metadata(cls, source: Source) -> list[Content]:
        """Retrieve content metadata from the source.

        Args:
            source: The source configuration.

        Returns:
            List of Content metadata objects.
        """
        pass

    @abstractmethod
    @classmethod
    async def get_src_content_type(cls, source: Source) -> ContentType:
        """Determine the content type of the source.

        Args:
            source: The source configuration.

        Returns:
            The ContentType enum value.
        """
        pass

    @abstractmethod
    @classmethod
    async def get_content_statistics(cls, source: Source) -> str:
        """Retrieve statistics about the source content.

        Args:
            source: The source configuration.

        Returns:
            String containing content statistics.
        """
        pass


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
        SourceType.hadoop: HadoopExtractConfigBuilder,
        SourceType.sparkstreaming: SparkStreamingExtractConfigBuilder,
        SourceType.s3: S3ExtractConfigBuilder,
        SourceType.csv: CsvExtractConfigBuilder,
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
        elif "hadoop:" in source:
            src = Source(
                source_type=SourceType.hadoop, connection_string=source.replace("hadoop:", "")
            )
        elif "spark:" in source:
            src = Source(
                source_type=SourceType.sparkstreaming,
                connection_string=source.replace("spark:", ""),
            )
        elif "s3:" in source:
            src = Source(source_type=SourceType.s3, connection_string=source.replace("s3:", ""))
        elif "csv:" in source:
            src = Source(source_type=SourceType.csv, connection_string=source.replace("csv:", ""))
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
