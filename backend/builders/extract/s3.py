"""S3 extract configuration builder."""

from models.extract import Content, ContentType, Source

from .base import BaseExtractConfigBuilder


class S3ExtractConfigBuilder(BaseExtractConfigBuilder):
    """Builder for S3 source configurations.

    Extracts metadata from S3 sources.
    """

    @classmethod
    async def get_content_metadata(cls, source: Source) -> list[Content]:
        """Extract content metadata from S3 source."""
        raise NotImplementedError("Metadata extraction not implemented for S3 sources.")

    @classmethod
    async def get_src_content_type(cls, source: Source) -> ContentType:
        """Get content type for S3 source.

        Args:
            source: S3 source configuration.

        Returns:
            ContentType for S3.
        """
        raise NotImplementedError("Content type extraction not implemented for S3 sources.")

    @classmethod
    async def get_content_statistics(cls, source: Source) -> dict:
        """Retrieve statistics about the source content.

        Args:
            source: The source configuration.

        Returns:
            Dictionary containing content statistics with
            any additional information about the source.
        """
        raise NotImplementedError("Content statistics extraction not implemented for S3 sources.")
