"""Module for extracting source information from user prompts."""

import asyncio

from models.extract import ContentType, Source, SourceType


async def extract_source_from_user_prompt(user_prompt: str) -> Source:
    """Extract source information from user prompt."""
    # Simulate an async operation (e.g., calling LLM)
    await asyncio.sleep(1)
    # Return a dummy Source object for demonstration purposes
    return Source(
        source_type=SourceType.PostgreSQL,
        connection_string="postgresql://user:password@localhost/dbname",
        content_type=ContentType.table,
        table_name="test_table",
    )
