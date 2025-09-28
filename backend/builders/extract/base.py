"""Base classes for extract configuration builders."""

from abc import ABC, abstractmethod

from models.extract import Content, ContentType, Source


class BaseExtractConfigBuilder(ABC):
    """
    Abstract base class for extract config builders.

    Subclasses must implement methods to extract metadata, content type, and statistics
    from various data sources.
    """

    @classmethod
    @abstractmethod
    async def get_content_metadata(cls, source: Source) -> list[Content]:
        """Retrieve content metadata from the source.

        Args:
            source: The source configuration.

        Returns:
            List of Content metadata objects for every content item (e.g., file, topic, etc.).
        """
        pass

    @classmethod
    @abstractmethod
    async def get_src_content_type(cls, source: Source) -> ContentType:
        """Determine the content type of the source.

        Args:
            source: The source configuration.

        Returns:
            The ContentType enum value.
        """
        pass

    @classmethod
    @abstractmethod
    async def get_content_statistics(cls, source: Source) -> dict:
        """Retrieve statistics about the source content.

        Args:
            source: The source configuration.

        Returns:
            Dictionary containing content statistics with
            any additional information about the source.
        """
        pass
