"""Extract configuration builders for various data sources."""

import logging
import sys
from typing import ClassVar

sys.path.insert(0, ".")

logger = logging.getLogger(__name__)

from models.extract import ExtractConfig, SourceType

from .base import BaseExtractConfigBuilder
from .clickhouse import ClickHouseExtractConfigBuilder
from .folder import FolderExtractConfigBuilder
from .kafka import KafkaExtractConfigBuilder
from .postgres import PostgresExtractConfigBuilder
from .s3 import S3ExtractConfigBuilder


class ExtractConfigBuilder:
    """Builder class for creating ExtractConfig instances from user prompts.

    This class uses LLM to extract Source from user prompt, then recognizes source types
    and delegates metadata extraction to specific builder classes.
    """

    source_to_builder_map: ClassVar[dict[SourceType, type[BaseExtractConfigBuilder]]] = {
        SourceType.folder: FolderExtractConfigBuilder,
        SourceType.kafka: KafkaExtractConfigBuilder,
        SourceType.PostgreSQL: PostgresExtractConfigBuilder,
        SourceType.ClickHouse: ClickHouseExtractConfigBuilder,
        SourceType.s3: S3ExtractConfigBuilder,
    }

    @classmethod
    async def from_user_prompt(cls, user_prompt: str) -> ExtractConfig:
        """Build an ExtractConfig from a user prompt using LLM.

        Args:
            user_prompt: The user's description of the data source.

        Returns:
            An ExtractConfig object with all fields populated.
        """
        logger.info("Building ExtractConfig from user prompt")
        # Use LLM to extract Source from user prompt
        src = await BaseExtractConfigBuilder.extract_source_from_user_prompt(user_prompt)
        logger.info(f"Extracted source: {src.source_type} - {src.connection_string}")

        # Now build the config from the source
        builder = cls.source_to_builder_map.get(src.source_type)
        if not builder:
            # Fallback to base builder with mocked data
            builder = BaseExtractConfigBuilder

        content_metadata = await builder.get_content_metadata(src)
        content_statistics = await builder.get_content_statistics(src)
        schedule = await builder.get_schedule(src)
        resources = await builder.get_resources(src)
        incremental = await builder.get_incremental(src)
        data_quality = await builder.get_data_quality(src)

        logger.info(f"ExtractConfig built successfully for {src.source_type}")
        return ExtractConfig(
            source_metadata=src,
            content_metadata=content_metadata,
            content_statistics=content_statistics,
            schedule=schedule,
            resources=resources,
            incremental=incremental,
            data_quality=data_quality,
        )
