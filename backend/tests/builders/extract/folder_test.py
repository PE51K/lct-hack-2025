"""Unit tests for FolderExtractConfigBuilder."""

import json
from pathlib import Path

import pytest

from builders.extract.folder import FolderExtractConfigBuilder
from models.extract import Content, ContentType, Source, SourceType


@pytest.fixture
def xml_source() -> Source:
    """Fixture for XML test data source."""
    return Source(
        source_type=SourceType.folder,
        connection_string=str(Path(__file__).parent / "test_data" / "xml"),
        content_type=ContentType.xml,
    )


@pytest.fixture
def csv_source() -> Source:
    """Fixture for CSV test data source."""
    return Source(
        source_type=SourceType.folder,
        connection_string=str(Path(__file__).parent / "test_data" / "csv"),
        content_type=ContentType.csv,
    )


@pytest.fixture
def json_source() -> Source:
    """Fixture for JSON test data source."""
    return Source(
        source_type=SourceType.folder,
        connection_string=str(Path(__file__).parent / "test_data" / "json"),
        content_type=ContentType.json,
    )


@pytest.mark.asyncio
async def test_get_src_content_type_xml(xml_source: Source):
    """Test get_src_content_type returns xml for XML folder."""
    content_type = await FolderExtractConfigBuilder.get_src_content_type(xml_source)
    assert content_type == ContentType.xml


@pytest.mark.asyncio
async def test_get_src_content_type_csv(csv_source: Source):
    """Test get_src_content_type returns csv for CSV folder."""
    content_type = await FolderExtractConfigBuilder.get_src_content_type(csv_source)
    assert content_type == ContentType.csv


@pytest.mark.asyncio
async def test_get_src_content_type_json(json_source: Source):
    """Test get_src_content_type returns json for JSON folder."""
    content_type = await FolderExtractConfigBuilder.get_src_content_type(json_source)
    assert content_type == ContentType.json


@pytest.mark.asyncio
async def test_get_content_metadata_xml(xml_source: Source):
    """Test get_content_metadata returns correct metadata for XML files."""
    metadata = await FolderExtractConfigBuilder.get_content_metadata(xml_source)
    assert len(metadata) == 2
    assert all(isinstance(item, Content) for item in metadata)

    # Check file names
    file_names = [item.message_name for item in metadata]
    assert "data1.xml" in file_names
    assert "data2.xml" in file_names

    # Check metamodels
    metamodel_dir = Path(__file__).parent / "test_metamodels" / "xml"
    expected_metamodel1 = json.loads((metamodel_dir / "metamodel1.json").read_text())
    expected_metamodel2 = json.loads((metamodel_dir / "metamodel2.json").read_text())

    metamodels = [item.metamodel for item in metadata]
    assert expected_metamodel1 in metamodels
    assert expected_metamodel2 in metamodels


@pytest.mark.asyncio
async def test_get_content_metadata_csv(csv_source: Source):
    """Test get_content_metadata returns correct metadata for CSV files."""
    metadata = await FolderExtractConfigBuilder.get_content_metadata(csv_source)
    assert len(metadata) == 2
    assert all(isinstance(item, Content) for item in metadata)

    # Check file names
    file_names = [item.message_name for item in metadata]
    assert "data1.csv" in file_names
    assert "data2.csv" in file_names

    # Check metamodels
    metamodel_dir = Path(__file__).parent / "test_metamodels" / "csv"
    expected_metamodel1 = json.loads((metamodel_dir / "metamodel1.json").read_text())
    expected_metamodel2 = json.loads((metamodel_dir / "metamodel2.json").read_text())

    metamodels = [item.metamodel for item in metadata]
    assert expected_metamodel1 in metamodels
    assert expected_metamodel2 in metamodels


@pytest.mark.asyncio
async def test_get_content_metadata_json(json_source: Source):
    """Test get_content_metadata returns correct metadata for JSON files."""
    metadata = await FolderExtractConfigBuilder.get_content_metadata(json_source)
    assert len(metadata) == 2
    assert all(isinstance(item, Content) for item in metadata)

    # Check file names
    file_names = [item.message_name for item in metadata]
    assert "data1.json" in file_names
    assert "data2.json" in file_names

    # Check metamodels
    metamodel_dir = Path(__file__).parent / "test_metamodels" / "json"
    expected_metamodel1 = json.loads((metamodel_dir / "metamodel1.json").read_text())
    expected_metamodel2 = json.loads((metamodel_dir / "metamodel2.json").read_text())

    metamodels = [item.metamodel for item in metadata]
    assert expected_metamodel1 in metamodels
    assert expected_metamodel2 in metamodels


@pytest.mark.asyncio
async def test_get_content_statistics_xml(xml_source: Source):
    """Test get_content_statistics returns statistics for XML folder."""
    stats = await FolderExtractConfigBuilder.get_content_statistics(xml_source)
    assert isinstance(stats, dict)


@pytest.mark.asyncio
async def test_get_content_statistics_csv(csv_source: Source):
    """Test get_content_statistics returns statistics for CSV folder."""
    stats = await FolderExtractConfigBuilder.get_content_statistics(csv_source)
    assert isinstance(stats, dict)


@pytest.mark.asyncio
async def test_get_content_statistics_json(json_source: Source):
    """Test get_content_statistics returns statistics for JSON folder."""
    stats = await FolderExtractConfigBuilder.get_content_statistics(json_source)
    assert isinstance(stats, dict)
