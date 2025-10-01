"""Kafka extract configuration builder."""

from models.extract import Content, Source

from .base import BaseExtractConfigBuilder


class KafkaExtractConfigBuilder(BaseExtractConfigBuilder):
    """Builder for Kafka source configurations.

    Extracts metadata from Kafka topics by sampling messages.
    """

    @classmethod
    async def get_content_metadata(cls, source: Source) -> list[Content]:
        """Extract content metadata from Kafka source."""
        raise NotImplementedError("Metadata extraction not implemented for Kafka sources.")
