"""Base classes for extract configuration builders."""

from langchain_openai import ChatOpenAI

from ai.llm import llm
from models.extract import (
    Content,
    DataQualityProfile,
    ExtractResourceConfig,
    ExtractSchedule,
    IncrementalConfig,
    Source,
)


class BaseExtractConfigBuilder:
    """
    Base class for extract config builders providing mockup implementations.

    This class provides default mockup implementations for all methods.
    Subclasses can override specific methods to provide real implementations.
    """

    @classmethod
    async def extract_source_from_user_prompt(cls, user_prompt: str) -> Source:
        """Extract Source object from user prompt using LLM.

        Args:
            user_prompt: The user's description of the data source.

        Returns:
            A Source object extracted from the prompt.
        """
        structured_llm = llm.with_structured_output(Source)

        system_prompt = """
        Extract the data source information from the user's prompt.
        Determine the source_type based on the description
        (e.g., folder, PostgreSQL, ClickHouse, kafka, s3).
        Extract connection_string if mentioned (e.g., database URL, file path).
        Extract table_name if it's a database table.
        If unsure, use 'na' for source_type.
        """

        return await structured_llm.ainvoke(
            [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        )

    @classmethod
    async def get_content_metadata(cls, source: Source) -> list[Content] | None:
        """Retrieve content metadata from the source.

        Args:
            source: The source configuration.

        Returns:
            List of Content metadata objects or None.
        """
        return None

    @classmethod
    async def get_content_statistics(cls, source: Source) -> dict | None:
        """Retrieve statistics about the source content.

        Args:
            source: The source configuration.

        Returns:
            Dictionary containing content statistics or None.
        """
        return None

    @classmethod
    async def get_schedule(cls, source: Source) -> ExtractSchedule:
        """Retrieve schedule configuration for the source.

        Args:
            source: The source configuration.

        Returns:
            ExtractSchedule configuration.
        """
        return ExtractSchedule()

    @classmethod
    async def get_resources(cls, source: Source) -> ExtractResourceConfig:
        """Retrieve resource configuration for the source.

        Args:
            source: The source configuration.

        Returns:
            ExtractResourceConfig configuration.
        """
        return ExtractResourceConfig()

    @classmethod
    async def get_incremental(cls, source: Source) -> IncrementalConfig:
        """Retrieve incremental configuration for the source.

        Args:
            source: The source configuration.

        Returns:
            IncrementalConfig configuration.
        """
        return IncrementalConfig()

    @classmethod
    async def get_data_quality(cls, source: Source) -> DataQualityProfile:
        """Retrieve data quality profile for the source.

        Args:
            source: The source configuration.

        Returns:
            DataQualityProfile configuration.
        """
        return DataQualityProfile()
