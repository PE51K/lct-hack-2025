"""Base classes for extract configuration builders."""

import logging

from ai.llm import llm
from models.extract import (
    Content,
    DataQualityProfile,
    ExtractResourceConfig,
    ExtractSchedule,
    IncrementalConfig,
    Source,
)

logger = logging.getLogger(__name__)


class BaseExtractConfigBuilder:
    """
    Base class for extract config builders providing mockup implementations.

    This class provides default mockup implementations for all methods.
    Subclasses can override specific methods to provide real implementations.
    """

    @classmethod
    async def extract_source_from_user_prompt(
        cls,
        user_prompt: str,
        old_source: Source | None = None,
        feedback_items: list | None = None,
        overall_feedback: str | None = None,
    ) -> Source:
        """Extract Source object from user prompt using LLM.

        Args:
            user_prompt: The user's description of the data source.
            old_source: Existing source to refine (optional).
            feedback_items: Specific feedback items (optional).
            overall_feedback: General feedback (optional).

        Returns:
            A Source object extracted from the prompt.
        """
        structured_llm = llm.with_structured_output(Source)

        if old_source:
            system_prompt = """
            Refine the existing data source information based on user feedback and new prompt.
            Start with the existing source configuration and modify only what's needed
            based on feedback.
            Determine the source_type based on the description
            (e.g., folder, PostgreSQL, ClickHouse, kafka, s3).
            Extract connection_string if mentioned (e.g., database URL, file path).
            Extract table_name if it's a database table.
            If unsure, use 'na' for source_type.
            """
            user_content = f"""
            Existing Source: {old_source.model_dump_json()}
            New Prompt: {user_prompt}
            """
            if feedback_items:
                user_content += (
                    f"\nFeedback Items: {[item.model_dump() for item in feedback_items]}"
                )
            if overall_feedback:
                user_content += f"\nOverall Feedback: {overall_feedback}"
        else:
            system_prompt = """
            Extract the data source information from the user's prompt.
            Determine the source_type based on the description
            (e.g., folder, PostgreSQL, ClickHouse, kafka, s3).
            Extract connection_string if mentioned (e.g., database URL, file path).
            Extract table_name if it's a database table.
            If unsure, use 'na' for source_type.
            """
            user_content = user_prompt

        source = await structured_llm.ainvoke(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ]
        )
        return source

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

    @classmethod
    async def get_batch_size(cls, source: Source) -> int:
        """Retrieve batch size configuration for the source.

        Args:
            source: The source configuration.

        Returns:
            Batch size for processing records.
        """
        return 1000  # Default batch size
