"""PostgreSQL extract configuration builder."""

from models.extract import Content, ContentType, Source

from . import BaseExtractConfigBuilder


class PostgresExtractConfigBuilder(BaseExtractConfigBuilder):
    """Builder for PostgreSQL source configurations.

    Extracts metadata from PostgreSQL sources.
    """

    @classmethod
    async def get_content_metadata(cls, source: Source) -> list[Content]:
        """Extract content metadata from PostgreSQL source."""
        raise NotImplementedError("Metadata extraction not implemented for PostgreSQL sources.")

    @classmethod
    async def get_src_content_type(cls, source: Source) -> ContentType:
        """Get content type for PostgreSQL source.

        Args:
            source: PostgreSQL source configuration.

        Returns:
            ContentType for PostgreSQL.
        """
        raise NotImplementedError("Content type extraction not implemented for PostgreSQL sources.")

    @classmethod
    async def get_content_statistics(cls, source: Source) -> str:
        """Get statistics for PostgreSQL source content.

        Args:
            source: PostgreSQL source configuration.

        Returns:
            String with content statistics.
        """
        raise NotImplementedError(
            "Content statistics extraction not implemented for PostgreSQL sources."
        )
