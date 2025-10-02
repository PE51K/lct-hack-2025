"""Unit tests for ExtractConfigBuilder."""

from pathlib import Path

import pytest

from builders.extract import ExtractConfigBuilder
from models.extract import ContentType, ExtractConfig, SourceType


@pytest.mark.asyncio
async def test_extract_config_builder_from_uri_xml():
    """Test ExtractConfigBuilder.from_uri for XML folder."""
    uri = f"file:{Path(__file__).parent / 'test_data' / 'xml'}"
    config = await ExtractConfigBuilder.from_uri(uri)

    assert isinstance(config, ExtractConfig)
    assert config.source_metadata.source_type == SourceType.folder
    assert config.content_type == ContentType.xml
    assert len(config.content_metadata) == 2
    assert isinstance(config.content_statistics, dict)


@pytest.mark.asyncio
async def test_extract_config_builder_from_uri_csv():
    """Test ExtractConfigBuilder.from_uri for CSV folder."""
    uri = f"file:{Path(__file__).parent / 'test_data' / 'csv'}"
    config = await ExtractConfigBuilder.from_uri(uri)

    assert isinstance(config, ExtractConfig)
    assert config.source_metadata.source_type == SourceType.folder
    assert config.content_type == ContentType.csv
    assert len(config.content_metadata) == 2
    assert isinstance(config.content_statistics, dict)


@pytest.mark.asyncio
async def test_extract_config_builder_from_uri_json():
    """Test ExtractConfigBuilder.from_uri for JSON folder."""
    uri = f"file:{Path(__file__).parent / 'test_data' / 'json'}"
    config = await ExtractConfigBuilder.from_uri(uri)

    assert isinstance(config, ExtractConfig)
    assert config.source_metadata.source_type == SourceType.folder
    assert config.content_type == ContentType.json
    assert len(config.content_metadata) == 2
    assert isinstance(config.content_statistics, dict)
