"""Base classes for extract configuration builders."""

from abc import ABC, abstractmethod

from models.extract import (
    Content,
    ContentType,
    DataQualityProfile,
    ExtractResourceConfig,
    ExtractSchedule,
    IncrementalConfig,
    Source,
)


class BaseExtractConfigBuilder(ABC):
    """
    Abstract base class for extract config builders.

    Subclasses must implement methods to extract metadata, content type, and statistics
    from various data sources.
    """

    @classmethod
    @abstractmethod
    async def get_content_metadata(cls, source: Source) -> Content:
        """Retrieve content metadata from the source.

        Args:
            source: The source configuration.

        Returns:
            Content metadata object.
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

    @classmethod
    @abstractmethod
    async def get_schedule(cls, source: Source) -> ExtractSchedule:
        """Retrieve schedule configuration for the source.

        Args:
            source: The source configuration.

        Returns:
            ExtractSchedule configuration.
        """
        pass

    @classmethod
    @abstractmethod
    async def get_resources(cls, source: Source) -> ExtractResourceConfig:
        """Retrieve resource configuration for the source.

        Args:
            source: The source configuration.

        Returns:
            ExtractResourceConfig configuration.
        """
        pass

    @classmethod
    @abstractmethod
    async def get_incremental(cls, source: Source) -> IncrementalConfig:
        """Retrieve incremental configuration for the source.

        Args:
            source: The source configuration.

        Returns:
            IncrementalConfig configuration.
        """
        pass

    @classmethod
    @abstractmethod
    async def get_data_quality(cls, source: Source) -> DataQualityProfile:
        """Retrieve data quality profile for the source.

        Args:
            source: The source configuration.

        Returns:
            DataQualityProfile configuration.
        """
        pass
