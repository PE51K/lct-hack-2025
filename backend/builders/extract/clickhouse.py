"""ClickHouse extract configuration builder."""

import logging

from models.extract import Content, Source

from .base import BaseExtractConfigBuilder

logger = logging.getLogger(__name__)


class ClickHouseExtractConfigBuilder(BaseExtractConfigBuilder):
    """Builder for ClickHouse source configurations.

    Extracts metadata from ClickHouse sources.
    """

    @classmethod
    async def get_content_metadata(cls, source: Source) -> list[Content]:
        """Extract content metadata from ClickHouse source."""
        raise NotImplementedError("Metadata extraction not implemented for ClickHouse sources.")
