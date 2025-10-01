"""S3 extract configuration builder."""

import logging

from models.extract import Content, Source

from .base import BaseExtractConfigBuilder

logger = logging.getLogger(__name__)


class S3ExtractConfigBuilder(BaseExtractConfigBuilder):
    """Builder for S3 source configurations.

    Extracts metadata from S3 sources.
    """

    @classmethod
    async def get_content_metadata(cls, source: Source) -> list[Content]:
        """Extract content metadata from S3 source."""
        raise NotImplementedError("Metadata extraction not implemented for S3 sources.")
