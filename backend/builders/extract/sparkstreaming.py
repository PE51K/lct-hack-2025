"""Spark Streaming extract configuration builder."""

from models.extract import Content, ContentType, Source

from . import BaseExtractConfigBuilder


class SparkStreamingExtractConfigBuilder(BaseExtractConfigBuilder):
    """Builder for Spark Streaming source configurations.

    Extracts metadata from Spark Streaming sources.
    """

    @classmethod
    async def get_content_metadata(cls, source: Source) -> list[Content]:
        """Extract content metadata from Spark Streaming source."""
        raise NotImplementedError(
            "Metadata extraction not implemented for Spark Streaming sources."
        )

    @classmethod
    async def get_src_content_type(cls, source: Source) -> ContentType:
        """Get content type for Spark Streaming source.

        Args:
            source: Spark Streaming source configuration.

        Returns:
            ContentType for Spark Streaming.
        """
        raise NotImplementedError(
            "Content type extraction not implemented for Spark Streaming sources."
        )

    @classmethod
    async def get_content_statistics(cls, source: Source) -> str:
        """Get statistics for Spark Streaming source content.

        Args:
            source: Spark Streaming source configuration.

        Returns:
            String with content statistics.
        """
        raise NotImplementedError(
            "Content statistics extraction not implemented for Spark Streaming sources."
        )
