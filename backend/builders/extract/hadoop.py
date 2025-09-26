"""Hadoop extract configuration builder."""

from models.extract import Content, ContentType, Source

from . import BaseExtractConfigBuilder


class HadoopExtractConfigBuilder(BaseExtractConfigBuilder):
    """Builder for Hadoop source configurations.

    Extracts metadata from Hadoop sources.
    """

    @classmethod
    async def get_content_metadata(cls, source: Source) -> list[Content]:
        """Extract content metadata from Hadoop source."""
        raise NotImplementedError("Metadata extraction not implemented for Hadoop sources.")

    @classmethod
    async def get_src_content_type(cls, source: Source) -> ContentType:
        """Get content type for Hadoop source.

        Args:
            source: Hadoop source configuration.

        Returns:
            ContentType for Hadoop.
        """
        raise NotImplementedError("Content type extraction not implemented for Hadoop sources.")

    @classmethod
    async def get_content_statistics(cls, source: Source) -> str:
        """Get statistics for Hadoop source content.

        Args:
            source: Hadoop source configuration.

        Returns:
            String with content statistics.
        """
        raise NotImplementedError(
            "Content statistics extraction not implemented for Hadoop sources."
        )
