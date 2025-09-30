"""Extract configuration builders for various data sources."""

import sys
from typing import ClassVar

sys.path.insert(0, ".")

from models.extract import ExtractConfig, Source, SourceType

from .base import BaseExtractConfigBuilder
from .clickhouse import ClickHouseExtractConfigBuilder
from .folder import FolderExtractConfigBuilder

# from .kafka import KafkaExtractConfigBuilder  # Commented out due to kafka package issues
from .postgres import PostgresExtractConfigBuilder
from .s3 import S3ExtractConfigBuilder


class ExtractConfigBuilder:
    """Builder class for creating ExtractConfig instances from URIs.

    This class recognizes source types from URI prefixes and delegates
    metadata extraction to specific builder classes.
    """

    source_to_builder_map: ClassVar[dict[SourceType, type[BaseExtractConfigBuilder]]] = {
        SourceType.folder: FolderExtractConfigBuilder,
        # SourceType.kafka: KafkaExtractConfigBuilder,  # Commented out due to kafka package issues
        SourceType.PostgreSQL: PostgresExtractConfigBuilder,
        SourceType.ClickHouse: ClickHouseExtractConfigBuilder,
        SourceType.s3: S3ExtractConfigBuilder,
    }

    @classmethod
    async def from_source(cls, src: Source) -> ExtractConfig:
        """Build an ExtractConfig from a URI.

        For now, returns a mock ExtractConfig.

        Args:
            src: The source object.

        Returns:
            A mock ExtractConfig object.
        """
        # src.content_type = await cls.source_to_builder_map[src.source_type].get_src_content_type(
        #     src
        # )
        # content_metadata = await cls.source_to_builder_map[src.source_type].get_content_metadata(
        #     src
        # )
        # content_statistics = await cls.source_to_builder_map[
        #     src.source_type
        # ].get_content_statistics(src)

        # return ExtractConfig(
        #     source_metadata=src,
        #     content_metadata=content_metadata,
        #     content_statistics=content_statistics,
        # )

        # Mock implementation
        import asyncio

        from models.extract import Attribute, Content

        await asyncio.sleep(1)
        return ExtractConfig(
            source_metadata=src,
            content_metadata=Content(
                message_name="mock_data",
                metamodel=[
                    Attribute(
                        order_no=1,
                        column_name="id",
                        data_type="integer",
                        is_nullable=False,
                        character_maximum_length=0,
                        numeric_precision=10,
                        numeric_scale=0,
                    ),
                    Attribute(
                        order_no=2,
                        column_name="name",
                        data_type="character varying",
                        is_nullable=False,
                        character_maximum_length=255,
                        numeric_precision=0,
                        numeric_scale=0,
                    ),
                ],
            ),
            content_statistics={"total_files": 1, "total_size": 1024},
        )
