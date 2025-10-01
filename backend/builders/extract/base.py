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
    async def get_content_metadata(cls, source: Source) -> Content:
        """Retrieve content metadata from the source.

        Args:
            source: The source configuration.

        Returns:
            Content metadata object.
        """
        # Mocked data
        return Content(
            message_name="mock_content",
            is_complex_nesting_present=False,
            metamodel=[],
        )

    @classmethod
    async def get_src_content_type(cls, source: Source) -> ContentType:
        """Determine the content type of the source.

        Args:
            source: The source configuration.

        Returns:
            The ContentType enum value.
        """
        # Mocked data
        return ContentType.na

    @classmethod
    async def get_content_statistics(cls, source: Source) -> dict:
        """Retrieve statistics about the source content.

        Args:
            source: The source configuration.

        Returns:
            Dictionary containing content statistics with
            any additional information about the source.
        """
        # Mocked data
        return {"total_files": 0, "total_size_mb": 0.0}

    @classmethod
    async def get_schedule(cls, source: Source) -> ExtractSchedule:
        """Retrieve schedule configuration for the source.

        Args:
            source: The source configuration.

        Returns:
            ExtractSchedule configuration.
        """
        # Mocked data
        return ExtractSchedule()

    @classmethod
    async def get_resources(cls, source: Source) -> ExtractResourceConfig:
        """Retrieve resource configuration for the source.

        Args:
            source: The source configuration.

        Returns:
            ExtractResourceConfig configuration.
        """
        # Mocked data
        return ExtractResourceConfig()

    @classmethod
    async def get_incremental(cls, source: Source) -> IncrementalConfig:
        """Retrieve incremental configuration for the source.

        Args:
            source: The source configuration.

        Returns:
            IncrementalConfig configuration.
        """
        # Mocked data
        return IncrementalConfig()

    @classmethod
    async def get_data_quality(cls, source: Source) -> DataQualityProfile:
        """Retrieve data quality profile for the source.

        Args:
            source: The source configuration.

        Returns:
            DataQualityProfile configuration.
        """
        # Mocked data
        return DataQualityProfile()
