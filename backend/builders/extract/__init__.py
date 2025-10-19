"""Extract configuration builders for various data sources."""

import logging
import sys
from pathlib import Path
from typing import ClassVar

from urllib.parse import urlparse

sys.path.insert(0, ".")

from models.app.update_etl import FeedbackItem
from models.extract import ExtractConfig, Source, SourceType

from .base import BaseExtractConfigBuilder
from .clickhouse import ClickHouseExtractConfigBuilder
from .folder import FolderExtractConfigBuilder
from .kafka import KafkaExtractConfigBuilder
from .postgres import PostgresExtractConfigBuilder
from .s3 import S3ExtractConfigBuilder

logger = logging.getLogger(__name__)


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
    async def from_user_prompt(
        cls,
        user_prompt: str,
        old_extract_config: ExtractConfig | None = None,
        feedback_items: list[FeedbackItem] | None = None,
        overall_feedback: str | None = None,
    ) -> ExtractConfig:
        """Build an ExtractConfig from a user prompt using LLM.

        Args:
            user_prompt: The user's description of the data source.
            old_extract_config: Existing config to refine (optional).
            feedback_items: Specific feedback items for extract (optional).
            overall_feedback: General feedback (optional).

        Returns:
            An ExtractConfig object with all fields populated.
        """
        # Use LLM to extract Source from user prompt
        old_source = old_extract_config.source_metadata if old_extract_config else None
        src = await BaseExtractConfigBuilder.extract_source_from_user_prompt(
            user_prompt, old_source, feedback_items, overall_feedback
        )
        logger.debug(f"Extracted source from user prompt: {src}")

        # Now build the config from the source
        builder = cls.source_to_builder_map.get(src.source_type)
        if not builder:
            # Fallback to base builder with mocked data
            builder = BaseExtractConfigBuilder
        logger.debug(f"Using builder {builder.__name__} for source type {src.source_type}")

        content_metadata = await builder.get_content_metadata(src)
        logger.debug(f"Content metadata: {content_metadata}")
        content_statistics = await builder.get_content_statistics(src)
        logger.debug(f"Content statistics: {content_statistics}")
        schedule = await builder.get_schedule(src)
        logger.debug(f"Schedule: {schedule}")
        resources = await builder.get_resources(src)
        logger.debug(f"Resources: {resources}")
        incremental = await builder.get_incremental(src)
        logger.debug(f"Incremental: {incremental}")
        data_quality = await builder.get_data_quality(src)
        logger.debug(f"Data quality: {data_quality}")
        batch_size = await builder.get_batch_size(src)
        logger.debug(f"Batch size: {batch_size}")
        sample_records = await builder.get_sample_records(src)
        logger.debug(f"Sample records collected: {len(sample_records) if sample_records else 0}")

        return ExtractConfig(
            source_metadata=src,
            content_metadata=content_metadata,
            content_statistics=content_statistics,
            schedule=schedule,
            resources=resources,
            incremental=incremental,
            data_quality=data_quality,
            batch_size=batch_size,
            sample_records=sample_records,
        )

    @classmethod
    async def from_uri(cls, uri: str) -> ExtractConfig:
        """Build an ExtractConfig directly from a concrete source URI.

        Currently supports local filesystem URIs (file:// or absolute paths).

        Args:
            uri: Pointer to the data source.

        Returns:
            An ExtractConfig built using the appropriate builder.

        Raises:
            ValueError: If the URI scheme is not supported.
        """
        if not uri:
            raise ValueError("URI must be provided")

        parsed = urlparse(uri)
        scheme = parsed.scheme or "file"
        logger.debug("Building extract config from URI '%s' (scheme=%s)", uri, scheme)

        if scheme == "file":
            # Support both file:/absolute/path and plain absolute/relative paths
            path_str = uri[5:] if uri.startswith("file:") else uri
            # Remove leading slashes introduced by file://
            if path_str.startswith("//"):
                path_str = path_str[2:]
            target_path = Path(path_str).expanduser().resolve()
            if not target_path.exists():
                raise ValueError(f"Path does not exist: {target_path}")

            source = Source(
                source_type=SourceType.folder,
                connection_string=f"file:{target_path.as_posix()}",
            )
            builder_cls = cls.source_to_builder_map.get(SourceType.folder, BaseExtractConfigBuilder)
        else:
            raise ValueError(f"Unsupported URI scheme: {scheme}")

        logger.debug("Using builder %s for URI %s", builder_cls.__name__, uri)

        content_metadata = await builder_cls.get_content_metadata(source)
        logger.debug("Content metadata: %s", content_metadata)
        content_statistics = await builder_cls.get_content_statistics(source)
        logger.debug("Content statistics: %s", content_statistics)
        schedule = await builder_cls.get_schedule(source)
        logger.debug("Schedule: %s", schedule)
        resources = await builder_cls.get_resources(source)
        logger.debug("Resources: %s", resources)
        incremental = await builder_cls.get_incremental(source)
        logger.debug("Incremental: %s", incremental)
        data_quality = await builder_cls.get_data_quality(source)
        logger.debug("Data quality: %s", data_quality)
        batch_size = await builder_cls.get_batch_size(source)
        logger.debug("Batch size: %s", batch_size)
        sample_records = await builder_cls.get_sample_records(source)
        logger.debug(
            "Sample records collected: %s",
            len(sample_records) if sample_records else 0,
        )

        return ExtractConfig(
            source_metadata=source,
            content_metadata=content_metadata,
            content_statistics=content_statistics,
            schedule=schedule,
            resources=resources,
            incremental=incremental,
            data_quality=data_quality,
            batch_size=batch_size,
            sample_records=sample_records,
        )
