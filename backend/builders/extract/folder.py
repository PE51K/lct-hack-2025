"""Folder extract configuration builder."""

from models.extract import Content, ContentType, Source

from . import BaseExtractConfigBuilder


class FolderExtractConfigBuilder(BaseExtractConfigBuilder):
    """Builder for folder source configurations.

    Extracts metadata from folder sources.
    """

    @classmethod
    async def get_content_metadata(cls, source: Source) -> list[Content]:
        """Extract content metadata from folder source."""
        raise NotImplementedError("Metadata extraction not implemented for folder sources.")

    @classmethod
    async def get_src_content_type(cls, source: Source) -> ContentType:
        """Get content type for folder source.

        Args:
            source: Folder source configuration.

        Returns:
            ContentType for folder.
        """
        raise NotImplementedError("Content type extraction not implemented for folder sources.")

    @classmethod
    async def get_content_statistics(cls, source: Source) -> str:
        """Get statistics for folder source content.

        Args:
            source: Folder source configuration.

        Returns:
            String with content statistics.
        """
        raise NotImplementedError(
            "Content statistics extraction not implemented for folder sources."
        )
