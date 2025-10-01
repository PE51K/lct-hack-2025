"""Folder extract configuration builder."""

import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from defusedxml import ElementTree

from core.logging import setup_logger
from models.extract import (
    Attribute,
    Content,
    ContentType,
    PostgreSqlDataType,
    Source,
)

from .base import BaseExtractConfigBuilder


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

    def analyze_xml_folder(self, folder_path: Path) -> tuple[XMLStructureAnalysis, list[str]]:
        """
        Analyze folder with XML files.

        Args:
            folder_path: Path to folder with XML files

        Returns:
            Tuple of overall analysis and list of processed files
        """
        xml_files = list(folder_path.glob("*.xml"))

        if not xml_files:
            return XMLStructureAnalysis(
                fields=[], total_records=0, max_depth=0, unique_elements=0, file_size_bytes=0
            ), []

        # Analyze first few files to get schema
        sample_files = xml_files[: min(3, len(xml_files))]

        combined_fields = {}
        total_records = 0
        total_size = 0
        max_depth = 0
        processed_files = []

        for xml_file in sample_files:
            try:
                analysis = self.analyze_xml_file(xml_file)
                total_records += analysis.total_records
                total_size += analysis.file_size_bytes
                max_depth = max(max_depth, analysis.max_depth)
                processed_files.append(xml_file.name)

                # Combine fields from different files
                for field in analysis.fields:
                    if field.xpath in combined_fields:
                        # Merge values and update statistics
                        existing_field = combined_fields[field.xpath]
                        existing_field.sample_values.extend(field.sample_values)
                        existing_field.sample_values = existing_field.sample_values[
                            : self.max_sample_values
                        ]
                        existing_field.occurrence_count += field.occurrence_count
                        existing_field.max_length = max(existing_field.max_length, field.max_length)
                    else:
                        combined_fields[field.xpath] = field

            except Exception as e:
                print(f"Error analyzing file {xml_file}: {e}")

        # Extrapolate statistics to all files
        if sample_files:
            files_multiplier = len(xml_files) / len(sample_files)
            total_records = int(total_records * files_multiplier)
            total_size = sum(f.stat().st_size for f in xml_files)

        # Recalculate data types with all values
        for field in combined_fields.values():
            if field.sample_values:
                field.data_type = self.type_detector.detect_data_type(field.sample_values)

        return XMLStructureAnalysis(
            fields=list(combined_fields.values()),
            total_records=total_records,
            max_depth=max_depth,
            unique_elements=len(combined_fields),
            file_size_bytes=total_size,
        ), processed_files

    def analyze_xml_file(self, file_path: Path) -> XMLStructureAnalysis:
        """
        Analyze single XML file.

        Args:
            file_path: Path to XML file

        Returns:
            Structure analysis result
        """
        try:
            # Parse XML
            tree = ElementTree.parse(file_path)
            root = tree.getroot()

            # Basic information
            file_size = file_path.stat().st_size
            root_name = root.tag

            # Collect field information
            field_info = defaultdict(
                lambda: {"values": [], "count": 0, "is_attribute": False, "parent_path": ""}
            )

            # Recursive traversal of XML structure
            max_depth = self._analyze_element_recursive(root, "", field_info, 0)

            # Convert to XMLFieldInfo
            fields = []
            for xpath, info in field_info.items():
                if info["values"]:  # Only fields with values
                    field = XMLFieldInfo(
                        xpath=xpath,
                        element_name=xpath.split("/")[-1],
                        data_type=self.type_detector.detect_data_type(info["values"]),
                        sample_values=info["values"][: self.max_sample_values],
                        is_nullable=True,  # Default to nullable
                        max_length=max(len(str(v)) for v in info["values"])
                        if info["values"]
                        else 0,
                        is_attribute=info["is_attribute"],
                        parent_path=info["parent_path"],
                        occurrence_count=info["count"],
                    )
                    fields.append(field)

            # Estimate record count
            total_records = self._estimate_record_count(root)

            return XMLStructureAnalysis(
                fields=fields,
                total_records=total_records,
                max_depth=max_depth,
                unique_elements=len(fields),
                file_size_bytes=file_size,
                root_element=root_name,
            )

        except Exception as e:
            import logging

            logging.error(f"Error analyzing XML file {file_path}: {e}")
            return XMLStructureAnalysis(
                fields=[],
                total_records=0,
                max_depth=0,
                unique_elements=0,
                file_size_bytes=0,
                root_element="error",
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

        # Form XPath for current element
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
        # Look for repeating elements at second level
        second_level_counts = Counter()

        for child in root:
            for grandchild in child:
                second_level_counts[grandchild.tag] += 1

        if second_level_counts:
            # Take maximum count of identical elements
            return max(second_level_counts.values())
        else:
            # If no nesting, count root's children
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


class FolderExtractConfigBuilder(BaseExtractConfigBuilder):
    """Builder for folder source configurations.

    Extracts metadata from folder sources.
    """

    @classmethod
    async def get_content_metadata(cls, source: Source) -> list[Content]:
        """Extract content metadata from folder source."""
        folder_path = Path(source.connection_string.replace("//", "").replace("file:", ""))

        if not folder_path.exists():
            return [Content(message_name="empty_folder", metamodel=[])]

        # Determine content type
        content_type = await cls.get_src_content_type(source)

        if content_type == ContentType.xml:
            content = await cls._analyze_xml_folder(folder_path)
            return [content]
        else:
            return [
                Content(
                    message_name=folder_path.name, is_complex_nesting_present=False, metamodel=[]
                )
            ]

    @classmethod
    async def _analyze_xml_folder(cls, folder_path: Path) -> Content:
        """Analyze XML files in folder using full parser."""
        logger = await setup_logger(__name__)
        xml_files = list(folder_path.glob("*.xml"))

        if not xml_files:
            return Content(message_name="no_xml_files", metamodel=[])

        await logger.info(f"Analyzing XML folder: {folder_path}")
        await logger.info(f"Found XML files: {len(xml_files)}")

        # Use full XML parser
        xml_parser = XMLParser(max_sample_values=20)
        analysis, processed_files = xml_parser.analyze_xml_folder(folder_path)

        await logger.info(f"Processed files: {len(processed_files)}")
        await logger.info(f"Found unique fields: {analysis.unique_elements}")
        await logger.info(f"Estimated records: {analysis.total_records}")
        await logger.info(f"Maximum depth: {analysis.max_depth}")

        # Convert analysis results to attributes
        attributes = xml_parser.convert_to_extract_attributes(analysis)

        # Determine nesting complexity
        is_complex = analysis.max_depth > 3 or analysis.unique_elements > 20

        return Content(
            message_name=f"xml_files_{len(xml_files)}",
            is_complex_nesting_present=is_complex,
            metamodel=attributes,
        )

    @classmethod
    async def _analyze_xml_folder_simple(cls, folder_path: Path) -> Content:
        """Simple analysis of XML files as fallback."""
        xml_files = list(folder_path.glob("*.xml"))

        if not xml_files:
            return Content(message_name="no_xml_files", metamodel=[])

        # Analyze first XML file to get basic structure
        sample_file = xml_files[0]
        attributes = []

        tree = ElementTree.parse(sample_file)
        root = tree.getroot()

        order = 1
        analyzed_tags = set()

        # Recursively traverse XML structure
        for elem in root.iter():
            if elem.tag not in analyzed_tags and elem.text and elem.text.strip():
                attr = Attribute(
                    order_no=order,
                    column_name=elem.tag.replace(":", "_").replace("-", "_"),
                    data_type=cls._detect_xml_data_type(elem.text.strip()),
                    is_nullable=True,
                    character_maximum_length=255,
                    numeric_precision=10,
                    numeric_scale=0,
                )
                attributes.append(attr)
                analyzed_tags.add(elem.tag)
                order += 1

                if order > 50:  # Limit for performance
                    break

        return Content(
            message_name=f"xml_files_{len(xml_files)}_simple",
            is_complex_nesting_present=True,
            metamodel=attributes,
        )

    @classmethod
    def _detect_xml_data_type(cls, value: str) -> str:
        """Detect data type from XML value."""
        try:
            # Try to determine type
            if value.lower() in ["true", "false"]:
                return "boolean"

            # Try number
            if "." in value:
                float(value)
                return "numeric"
            else:
                int(value)
                return "integer"

        except ValueError:
            pass

        # Default to text
        return "text"
