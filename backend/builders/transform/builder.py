"""Transform configuration builder."""

import logging

from models.ddl import DDL

logger = logging.getLogger(__name__)
from models.extract import ExtractConfig
from models.load import LoadConfig
from models.transform import TransformConfig


class TransformConfigBuilder:
    """Builder for TransformConfig."""

    async def __call__(
        self, ddl: DDL, extract_config: ExtractConfig, load_config: LoadConfig, prompt: str
    ) -> TransformConfig:
        """Build TransformConfig from DDL, ExtractConfig, LoadConfig and prompt.

        Args:
            ddl: The DDL configuration.
            extract_config: The extract configuration.
            load_config: The load configuration.
            prompt: User prompt.

        Returns:
            TransformConfig with mocked data.
        """
        logger.info("Building TransformConfig from configs and prompt")
        # Mocked data
        transform_config = TransformConfig(
            identity_keys=["id"],
            aggregate_keys=[],
            versioning_field=None,
            transformation_rules=[],
            validation_rules=[],
            business_rules=[],
            data_type_mappings=[],
            processing_mode="batch",
            window_size_minutes=None,
            late_arrival_threshold_minutes=60,
            output_format="table",
            partitioning_strategy=None,
            sorting_keys=[],
        )
        logger.info(f"TransformConfig built with {len(transform_config.transformation_rules)} rules")
        return transform_config
