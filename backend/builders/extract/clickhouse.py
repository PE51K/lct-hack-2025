"""ClickHouse extract configuration builder."""

from models.extract import Content, ContentType, Source

from . import BaseExtractConfigBuilder


class ClickHouseExtractConfigBuilder(BaseExtractConfigBuilder):
    """Builder for ClickHouse source configurations.

    Extracts metadata from ClickHouse sources.
    """

    @classmethod
    async def get_content_metadata(cls, source: Source) -> list[Content]:
        """Extract content metadata from ClickHouse source."""
        raise NotImplementedError("Metadata extraction not implemented for ClickHouse sources.")

    @classmethod
    async def get_src_content_type(cls, source: Source) -> ContentType:
        """Get content type for ClickHouse source.

        Args:
            source: ClickHouse source configuration.

        Returns:
            ContentType for ClickHouse.
        """
        raise NotImplementedError("Content type extraction not implemented for ClickHouse sources.")

    @classmethod
    async def get_content_statistics(cls, source: Source) -> str:
        """Get statistics for ClickHouse source content.

        Args:
            source: ClickHouse source configuration.

        Returns:
            String with content statistics.
        """
        raise NotImplementedError(
            "Content statistics extraction not implemented for ClickHouse sources."
        )
