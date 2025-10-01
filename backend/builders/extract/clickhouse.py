"""ClickHouse extract configuration builder."""

from models.extract import Content, Source

from .base import BaseExtractConfigBuilder


class ClickHouseExtractConfigBuilder(BaseExtractConfigBuilder):
    """Builder for ClickHouse source configurations.

    Extracts metadata from ClickHouse sources.
    """

    @classmethod
    async def get_content_metadata(cls, source: Source) -> list[Content]:
        """Extract content metadata from ClickHouse source."""
        raise NotImplementedError("Metadata extraction not implemented for ClickHouse sources.")
