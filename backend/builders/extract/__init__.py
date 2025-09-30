"""Extract configuration builders for various data sources."""

import sys
from typing import ClassVar

sys.path.insert(0, ".")

from models.extract import ExtractConfig, Source, SourceType

from .base import BaseExtractConfigBuilder
from .folder import FolderExtractConfigBuilder

# Опциональные импорты для builders, которые требуют дополнительных зависимостей
try:
    from .postgres import PostgresExtractConfigBuilder
except ImportError:
    PostgresExtractConfigBuilder = None

try:
    from .clickhouse import ClickHouseExtractConfigBuilder
except ImportError:
    ClickHouseExtractConfigBuilder = None

try:
    from .kafka import KafkaExtractConfigBuilder  
except ImportError:
    KafkaExtractConfigBuilder = None

try:
    from .s3 import S3ExtractConfigBuilder
except ImportError:
    S3ExtractConfigBuilder = None


class ExtractConfigBuilder:
    """Builder class for creating ExtractConfig instances from URIs.

    This class recognizes source types from URI prefixes and delegates
    metadata extraction to specific builder classes.
    """

    # Динамическое создание карты builders только для доступных модулей
    @classmethod
    def _get_source_to_builder_map(cls):
        """Получение карты builders с проверкой доступности."""
        builder_map = {
            SourceType.folder: FolderExtractConfigBuilder,
        }
        
        # Добавляем опциональные builders если они доступны
        if PostgresExtractConfigBuilder is not None:
            builder_map[SourceType.PostgreSQL] = PostgresExtractConfigBuilder
            
        if ClickHouseExtractConfigBuilder is not None:
            builder_map[SourceType.ClickHouse] = ClickHouseExtractConfigBuilder
            
        if KafkaExtractConfigBuilder is not None:
            builder_map[SourceType.kafka] = KafkaExtractConfigBuilder
            
        if S3ExtractConfigBuilder is not None:
            builder_map[SourceType.s3] = S3ExtractConfigBuilder
            
        return builder_map

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

        # Получаем карту доступных builders
        builder_map = cls._get_source_to_builder_map()
        
        if src.source_type not in builder_map:
            raise ValueError(f"Builder для типа источника '{src.source_type}' не доступен")
        
        builder = builder_map[src.source_type]
        
        src.content_type = await builder.get_src_content_type(src)
        content_metadata = await builder.get_content_metadata(src)
        content_statistics = await builder.get_content_statistics(src)

        return ExtractConfig(
            source_metadata=src,
            content_metadata=content_metadata,
            content_statistics=content_statistics,
        )
