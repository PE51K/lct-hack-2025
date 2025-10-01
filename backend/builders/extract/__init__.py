"""Extract configuration builders for various data sources."""

import sys
from typing import ClassVar

sys.path.insert(0, ".")

from models.extract import ExtractConfig, Source, SourceType

from .base import BaseExtractConfigBuilder
# from .clickhouse import ClickHouseExtractConfigBuilder
# from .folder import FolderExtractConfigBuilder
# from .kafka import KafkaExtractConfigBuilder  # Commented out due to kafka package issues
# from .postgres import PostgresExtractConfigBuilder
# from .s3 import S3ExtractConfigBuilder


class ExtractConfigBuilder:
    """Builder class for creating ExtractConfig instances from URIs.

    This class recognizes source types from URI prefixes and delegates
    metadata extraction to specific builder classes.
    """

    source_to_builder_map: ClassVar[dict[SourceType, type[BaseExtractConfigBuilder]]] = {
        # SourceType.folder: FolderExtractConfigBuilder,
        # SourceType.kafka: KafkaExtractConfigBuilder,  # Commented out due to kafka package issues
        # SourceType.PostgreSQL: PostgresExtractConfigBuilder,
        # SourceType.ClickHouse: ClickHouseExtractConfigBuilder,
        # SourceType.s3: S3ExtractConfigBuilder,
    }

    @classmethod
    async def from_source(cls, src: Source) -> ExtractConfig:
        """Build an ExtractConfig from a Source.

        Args:
            src: The source object.

        Returns:
            An ExtractConfig object with all fields populated.
        """
        builder = cls.source_to_builder_map.get(src.source_type)
        if not builder:
            # Fallback to base builder with mocked data
            builder = BaseExtractConfigBuilder

        content_type = await builder.get_src_content_type(src)
        content_metadata = await builder.get_content_metadata(src)
        content_statistics = await builder.get_content_statistics(src)
        schedule = await builder.get_schedule(src)
        resources = await builder.get_resources(src)
        incremental = await builder.get_incremental(src)
        data_quality = await builder.get_data_quality(src)

        return ExtractConfig(
            source_metadata=src,
            content_metadata=content_metadata,
            content_statistics=content_statistics,
            schedule=schedule,
            resources=resources,
            incremental=incremental,
            data_quality=data_quality,
            content_type=content_type,
        )
