"""Folder extract configuration builder."""

import glob
import json
import logging
import os
from pathlib import Path
from typing import Any

import pandas as pd
from ydata_profiling import ProfileReport

from models.extract import Content, ContentType, Source

from .base import BaseExtractConfigBuilder


class FolderExtractConfigBuilder(BaseExtractConfigBuilder):
    """Builder for folder source configurations.

    Extracts metadata from folder sources.
    """

    @classmethod
    def _clean_profile_data(cls, profile_data: dict, exclude_keys: list[str] | None = None) -> dict:
        """Recursively remove specified keys from profile data."""
        if exclude_keys is None:
            exclude_keys = [
                "value_counts_without_nan",
                "value_counts_index_sorted",
                "value_counts",
                "value_counts_with_nan",
                "histogram_data",
                "histogram_frequency",
                "mini_histogram",
                "first_rows",
                "length_histogram",
                "histogram_length",
                "bin_edges",
                "character_counts",
                "category_alias_values",
                "block_alias_values",
                "block_alias_char_counts",
                "script_char_counts",
                "category_alias_char_counts",
                "word_counts",
                "histogram",
                "counts",
                "block_alias_counts",
                "category_alias_counts",
                "script_counts",
                "n_scripts",
                "n_characters_distinct",
            ]

        if isinstance(profile_data, dict):
            return {
                key: cls._clean_profile_data(value, exclude_keys)
                for key, value in profile_data.items()
                if key not in exclude_keys
            }
        elif isinstance(profile_data, list):
            return [cls._clean_profile_data(item, exclude_keys) for item in profile_data]
        else:
            return profile_data


    @classmethod
    async def get_content_metadata(cls, source: Source) -> list[Content]:
        """Extract content metadata from folder source."""
        folder_path = source.connection_string
        contents = []

        supported_extensions = ["*.csv", "*.json", "*.xml"]

        for extension in supported_extensions:
            pattern = os.path.join(folder_path, extension)
            for file_path in glob.glob(pattern):
                file_name = os.path.basename(file_path)

                if file_path.endswith(".csv"):
                    analysis_result = await cls._analyze_csv_file(file_path)
                    metamodel = await cls._convert_analysis_to_metamodel(analysis_result, file_name)
                elif file_path.endswith(".json") or file_path.endswith(".xml"):
                    metamodel = {"type": "object", "properties": {}, "required": []}
                content = Content(message_name=file_name, metamodel=metamodel)
                contents.append(content)
        return contents


    @classmethod
    async def _convert_analysis_to_metamodel(
        cls, analysis_result: dict[str, Any], file_name: str
    ) -> dict[str, Any]:
        """Convert analysis result to JSON Schema metamodel."""
        if "error" in analysis_result:
            return {"type": "object", "properties": {}, "required": []}

        properties = {}
        required = []

        # Use column information to create properties
        columns = analysis_result.get("columns", [])
        variables_data = analysis_result.get("variables", {})

        for column in columns:
            if column in variables_data:
                var_info = variables_data[column]
                # Determine type based on analysis
                inferred_type = await cls._infer_json_schema_type(var_info, column)
                properties[column] = {"type": inferred_type}
                # Consider all fields as required for simplicity
                required.append(column)
            else:
                # If no detailed information is available, use string as fallback
                properties[column] = {"type": "string"}
                required.append(column)

        return {"type": "object", "properties": properties, "required": required}


    @classmethod
    async def _infer_json_schema_type(cls, var_info: dict[str, Any], column_name: str) -> str:
        """Infer JSON Schema type from variable analysis with improved logic."""
        # Analyze type from variables
        var_type = var_info.get("type", "").lower()

        # Improved type determination logic
        if var_type in ["integer", "int"]:
            return "integer"
        elif var_type in ["float", "numeric", "number"]:
            return "number"
        elif var_type == "boolean" or var_type == "bool":
            return "boolean"
        else:
            # Heuristics based on column name
            if column_name.lower() in ["age", "year", "id"]:
                return "integer"
            else:
                return "string"


    @classmethod
    async def get_src_content_type(cls, source: Source) -> ContentType:
        """Get content type for folder source."""
        # Determine type based on content for folders
        folder_path = source.connection_string

        try:
            files = os.listdir(folder_path)
            # Check files in the folder
            if any(f.endswith(".csv") for f in files):
                return ContentType.csv
            elif any(f.endswith(".json") for f in files):
                return ContentType.json
            elif any(f.endswith(".xml") for f in files):
                return ContentType.xml
            else:
                return ContentType.na
        except Exception:
            return ContentType.na


    @classmethod
    async def get_content_statistics(cls, source: Source) -> dict:
        """Retrieve statistics about the source content."""
        folder_path = source.connection_string

        try:
            # CSV files in the folder
            csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

            if not csv_files:
                return {"error": "No CSV files found in folder"}

            # Analyze the first CSV file
            first_csv_file = csv_files[0]
            analysis_result = await cls._analyze_csv_file(first_csv_file)

            if "error" in analysis_result:
                return {
                    "error": analysis_result["error"],
                    "folder_path": folder_path,
                    "status": "analysis_failed",
                }

            # Create statistics in the expected format
            statistics = {
                "file_analyzed": os.path.basename(first_csv_file),
                "total_files": len(csv_files),
                "file_types": ["csv"],
                "analysis_summary": {
                    "row_count": analysis_result.get("row_count", 0),
                    "column_count": len(analysis_result.get("columns", [])),
                    "file_size": analysis_result.get("file_size", 0),
                    "variables": analysis_result.get("variables", 0),
                },
            }

            return statistics

        except Exception as e:
            logging.getLogger(__name__).error(f"Error getting statistics for {folder_path}: {e}")
            return {"error": str(e), "folder_path": folder_path, "status": "analysis_failed"}


    @classmethod
    async def _analyze_csv_file(cls, file_path: Path) -> dict[str, Any]:
        """Analyze CSV file with improved type detection."""
        try:
            sample_size = 10000
            separators = [",", ";", "\t", "|"]

            for sep in separators:
                try:
                    df = pd.read_csv(
                        file_path, sep=sep, on_bad_lines="skip", engine="python", nrows=sample_size
                    )
                    if df.shape[1] > 1:
                        break
                except Exception as e:
                    logging.getLogger(__name__).warning(
                        f"Failed to read CSV file {file_path} with separator '{sep}': {e}"
                    )
                    continue
            else:
                sep = ","
                df = pd.read_csv(
                    file_path, sep=sep, on_bad_lines="skip", engine="python", nrows=sample_size
                )

            # Create profile
            profile = ProfileReport(df, title="Profiling Report", explorative=True)
            profile_json = profile.to_json()
            data = json.loads(profile_json)
            cleaned_data = cls._clean_profile_data(data)

            return {
                "variables": cleaned_data.get("variables", {}),
                "table": data.get("table", {}),
                "columns": list(df.columns),
                "row_count": len(df),
                "file_size": os.path.getsize(file_path),
                "file_name": os.path.basename(file_path),
            }

        except Exception as e:
            logging.getLogger(__name__).error(f"Error analyzing CSV file {file_path}: {e}")
            return {"error": str(e)}
