"""S3 extract configuration builder."""

import logging
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass

import boto3
from defusedxml import ElementTree

from core.settings import settings
from models.extract import (
    Attribute,
    Content,
    ContentType,
    PostgreSqlDataType,
    Source,
)

from .base import BaseExtractConfigBuilder

logger = logging.getLogger(__name__)


@dataclass
class XMLFieldInfo:
    """Information about XML field."""

    xpath: str
    element_name: str
    data_type: PostgreSqlDataType
    sample_values: list[str]
    is_nullable: bool
    max_length: int
    is_attribute: bool = False
    parent_path: str = ""
    occurrence_count: int = 0


@dataclass
class XMLStructureAnalysis:
    """Result of XML structure analysis."""

    fields: list[XMLFieldInfo]
    total_records: int
    max_depth: int
    unique_elements: int
    file_size_bytes: int
    encoding: str = "utf-8"
    root_element: str = ""
    namespace_info: dict[str, str] = None


class XMLDataTypeDetector:
    """Data type detector for XML values."""

    @staticmethod
    def detect_data_type(values: list[str]) -> PostgreSqlDataType:
        """
        Determine data type based on sample values.

        Args:
            values: List of values for analysis

        Returns:
            Most suitable PostgreSQL data type
        """
        if not values:
            return PostgreSqlDataType.TEXT

        # Counters for different types
        type_counts = {
            "boolean": 0,
            "integer": 0,
            "numeric": 0,
            "date": 0,
            "timestamp": 0,
            "text": 0,
        }

        for value in values:
            if not value or not value.strip():
                continue

            value = value.strip()

            # Boolean
            if value.lower() in ["true", "false", "yes", "no", "1", "0"]:
                type_counts["boolean"] += 1
                continue

            # Integer
            if re.match(r"^-?\d+$", value):
                type_counts["integer"] += 1
                continue

            # Numeric (float/decimal)
            if re.match(r"^-?\d+\.\d+$", value):
                type_counts["numeric"] += 1
                continue

            # Date patterns
            if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
                type_counts["date"] += 1
                continue

            # Timestamp patterns
            if re.match(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}", value):
                type_counts["timestamp"] += 1
                continue

            # Everything else is text
            type_counts["text"] += 1

        # Determine predominant type
        max_type = max(type_counts.items(), key=lambda x: x[1])[0]

        type_mapping = {
            "boolean": PostgreSqlDataType.BOOLEAN,
            "integer": PostgreSqlDataType.INTEGER,
            "numeric": PostgreSqlDataType.NUMERIC,
            "date": PostgreSqlDataType.DATE,
            "timestamp": PostgreSqlDataType.TIMESTAMP,
            "text": PostgreSqlDataType.TEXT,
        }

        return type_mapping[max_type]


class XMLParser:
    """Full XML parser."""

    def __init__(self, max_sample_values: int = 10, max_depth: int = 20):
        """
        Initialize parser.

        Args:
            max_sample_values: Maximum number of sample values for analysis
            max_depth: Maximum depth for nesting analysis
        """
        self.max_sample_values = max_sample_values
        self.max_depth = max_depth
        self.type_detector = XMLDataTypeDetector()

    def analyze_xml_content(
        self, content: str, file_name: str, file_size: int
    ) -> XMLStructureAnalysis:
        """
        Analyze XML from string content.

        Args:
            content: XML content as string
            file_name: Name of the file for logging
            file_size: Size of the file in bytes

        Returns:
            Structure analysis result
        """
        root = ElementTree.fromstring(content)

        root_name = root.tag

        field_info = defaultdict(
            lambda: {"values": [], "count": 0, "is_attribute": False, "parent_path": ""}
        )

        max_depth = self._analyze_element_recursive(root, "", field_info, 0)

        fields = []
        for xpath, info in field_info.items():
            if info["values"]:
                field = XMLFieldInfo(
                    xpath=xpath,
                    element_name=xpath.split("/")[-1],
                    data_type=self.type_detector.detect_data_type(info["values"]),
                    sample_values=info["values"][: self.max_sample_values],
                    is_nullable=True,
                    max_length=max(len(str(v)) for v in info["values"]) if info["values"] else 0,
                    is_attribute=info["is_attribute"],
                    parent_path=info["parent_path"],
                    occurrence_count=info["count"],
                )
                fields.append(field)

        total_records = self._estimate_record_count(root)

        return XMLStructureAnalysis(
            fields=fields,
            total_records=total_records,
            max_depth=max_depth,
            unique_elements=len(fields),
            file_size_bytes=file_size,
            root_element=root_name,
        )

    def _analyze_element_recursive(
        self, element: ET.Element, current_path: str, field_info: dict, depth: int
    ) -> int:
        """
        Recursive analysis of XML element.

        Args:
            element: XML element
            current_path: Current XPath
            field_info: Dictionary for collecting field information
            depth: Current depth

        Returns:
            Maximum depth reached
        """
        if depth > self.max_depth:
            return depth

        element_path = f"{current_path}/{element.tag}" if current_path else element.tag
        max_depth_reached = depth

        # Analyze element attributes
        for attr_name, attr_value in element.attrib.items():
            attr_path = f"{element_path}/@{attr_name}"
            field_info[attr_path]["values"].append(attr_value)
            field_info[attr_path]["count"] += 1
            field_info[attr_path]["is_attribute"] = True
            field_info[attr_path]["parent_path"] = element_path

        # Analyze text content
        if element.text and element.text.strip():
            field_info[element_path]["values"].append(element.text.strip())
            field_info[element_path]["count"] += 1
            field_info[element_path]["parent_path"] = current_path

        # Recursively analyze child elements
        for child in element:
            child_depth = self._analyze_element_recursive(
                child, element_path, field_info, depth + 1
            )
            max_depth_reached = max(max_depth_reached, child_depth)

        return max_depth_reached

    def _estimate_record_count(self, root: ET.Element) -> int:
        """
        Estimate number of records in XML document.

        Args:
            root: Root XML element

        Returns:
            Approximate number of records
        """
        second_level_counts = Counter()

        for child in root:
            for grandchild in child:
                second_level_counts[grandchild.tag] += 1

        if second_level_counts:
            return max(second_level_counts.values())
        else:
            return len(list(root))

    def convert_to_extract_attributes(self, analysis: XMLStructureAnalysis) -> list[Attribute]:
        """
        Convert analysis results to Attribute format for ExtractConfig.

        Args:
            analysis: XML analysis result

        Returns:
            List of attributes in Extract model format
        """
        attributes = []

        for i, field in enumerate(analysis.fields, 1):
            attr = Attribute(
                order_no=i,
                column_name=field.xpath.replace("/", "_").replace("@", "attr_"),
                data_type=field.data_type,
                is_nullable=field.is_nullable,
                character_maximum_length=min(field.max_length, 65535)
                if field.data_type
                in [
                    PostgreSqlDataType.TEXT,
                    PostgreSqlDataType.VARCHAR,
                    PostgreSqlDataType.CHARACTER_VARYING,
                ]
                else None,
                numeric_precision=10
                if field.data_type
                in [
                    PostgreSqlDataType.INTEGER,
                    PostgreSqlDataType.NUMERIC,
                    PostgreSqlDataType.DECIMAL,
                ]
                else None,
                numeric_scale=2
                if field.data_type in [PostgreSqlDataType.NUMERIC, PostgreSqlDataType.DECIMAL]
                else 0,
            )
            attributes.append(attr)

        return attributes


class S3ExtractConfigBuilder(BaseExtractConfigBuilder):
    """Builder for S3 source configurations.

    Extracts metadata from S3 sources.
    """

    @classmethod
    async def get_content_metadata(cls, source: Source) -> list[Content]:
        """Extract content metadata from S3 source."""
        # Use S3-compatible storage with settings fallback
        endpoint_url = source.connection_string or settings.s3.endpoint_url
        access_key = source.access_key or settings.s3.access_key_id
        secret_key = source.secret_key or settings.s3.secret_access_key

        # Transform localhost URLs to Docker network hostnames when running in Docker
        # This is CRITICAL for Airflow tasks running inside Docker containers
        if endpoint_url and "localhost:9000" in endpoint_url:
            endpoint_url = endpoint_url.replace("localhost:9000", "test-minio:9000")
            # IMPORTANT: Update source.connection_string so DAG generation uses correct endpoint
            source.connection_string = endpoint_url
            logger.info(f"Transformed localhost endpoint to Docker network: {endpoint_url}")
        elif endpoint_url and "127.0.0.1:9000" in endpoint_url:
            endpoint_url = endpoint_url.replace("127.0.0.1:9000", "test-minio:9000")
            # IMPORTANT: Update source.connection_string so DAG generation uses correct endpoint
            source.connection_string = endpoint_url
            logger.info(f"Transformed 127.0.0.1 endpoint to Docker network: {endpoint_url}")

        s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=settings.s3.region,
        )
        bucket = source.bucket_name
        prefix = source.table_name if source.table_name and source.table_name != "na" else ""

        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

        if not response.get("Contents"):
            return [Content(message_name="empty_s3_prefix", metamodel=[])]

        xml_objects = [obj for obj in response["Contents"] if obj["Key"].endswith(".xml")]

        if not xml_objects:
            return None

        contents = []
        xml_parser = XMLParser(max_sample_values=20)

        # Limit analysis: only first 3 files, skip files larger than 100MB
        MAX_FILES_TO_ANALYZE = 3
        MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB
        MAX_CONTENT_READ_BYTES = 10 * 1024 * 1024  # Read only first 10MB for large files

        files_analyzed = 0
        for obj in xml_objects:
            if files_analyzed >= MAX_FILES_TO_ANALYZE:
                logger.info(f"Reached max files to analyze ({MAX_FILES_TO_ANALYZE}), stopping")
                break

            key = obj["Key"]
            file_size = obj["Size"]

            # Skip very large files
            if file_size > MAX_FILE_SIZE_BYTES:
                logger.warning(f"Skipping large file {key} ({file_size / (1024**2):.1f} MB) - exceeds {MAX_FILE_SIZE_BYTES / (1024**2):.0f} MB limit")
                continue

            try:
                logger.info(f"Analyzing XML file: {key} ({file_size / (1024**2):.2f} MB)")
                response = s3.get_object(Bucket=bucket, Key=key)

                # For files larger than 5MB, read only first portion for structure analysis
                if file_size > 5 * 1024 * 1024:
                    logger.info(f"Large file detected, reading first {MAX_CONTENT_READ_BYTES / (1024**2):.0f}MB for structure analysis")
                    content = response["Body"].read(MAX_CONTENT_READ_BYTES).decode("utf-8", errors="ignore")
                    # Add closing tag if content was truncated
                    if not content.rstrip().endswith(">"):
                        content += "\n</root>"
                else:
                    content = response["Body"].read().decode("utf-8")

                analysis = xml_parser.analyze_xml_content(content, key, file_size)
                attributes = xml_parser.convert_to_extract_attributes(analysis)
                is_complex = analysis.max_depth > 3 or analysis.unique_elements > 20

                cnt = Content(
                    message_name=key,
                    is_complex_nesting_present=is_complex,
                    content_type=ContentType.xml,
                    metamodel=attributes,
                )
                contents.append(cnt)
                files_analyzed += 1
                logger.info(f"Successfully analyzed {key}")

            except Exception as e:
                logger.error(f"Error analyzing XML file {key}: {e}", exc_info=True)
                # Continue with other files
                continue

        if not contents:
            logger.warning("No XML files could be analyzed")
            return None

        return contents
