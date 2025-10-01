"""
Integrated DAG Generator for the main application.

This module provides a simple interface for creating ETL DAG
from the main LCT-hack-2025 application.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any

# Add path to dag_generation module
sys.path.append(str(Path(__file__).parent.parent))

from dag_generation import ETLDAGGenerationSystem

from models.extract import ExtractConfig
from models.load import LoadConfig
from models.transform import TransformConfig

logger = logging.getLogger(__name__)


class IntegratedDAGGenerator:
    """
    Integrated DAG generator for the main application.

    Provides a simple interface for creating ETL pipelines
    using existing builders and project models.
    """

    def __init__(self, output_dir: str = "generated_dags"):
        """
        Generator initialization.

        Args:
            output_dir: Directory for saving generated DAGs
        """
        self.dag_system = ETLDAGGenerationSystem(output_base_dir=output_dir)
        self.output_dir = Path(output_dir)

    async def create_dag_from_url(
        self,
        source_url: str,
        pipeline_name: str,
        owner: str = "data_team",
        team: str = "analytics",
        description: str = "Generated ETL pipeline",
    ) -> dict[str, Any]:
        """
        Creating DAG from data source URL.

        Args:
            source_url: URL or path to data source
            pipeline_name: Pipeline name
            owner: Pipeline owner
            team: Team
            description: Pipeline description

        Returns:
            Result of DAG creation with metadata
        """
        try:
            logger.info(f"Creating DAG: {pipeline_name} from source: {source_url}")
            print(f"🚀 Creating DAG: {pipeline_name}")
            print(f"📂 Source: {source_url}")

            # Create complete pipeline
            result = await self.dag_system.create_complete_etl_pipeline(
                source_url=source_url,
                pipeline_name=pipeline_name,
                owner=owner,
                team=team,
                description=description,
            )

            if result["success"]:
                print("✅ DAG created successfully!")
                print(f"📁 Files saved in: {result['output_directory']}")
                return {
                    "success": True,
                    "pipeline_id": result["pipeline_id"],
                    "output_directory": result["output_directory"],
                    "dag_file": result["files"]["dag_file"],
                    "config_file": result["files"]["config_file"],
                    "ai_recommendations_count": len(result.get("ai_recommendations", [])),
                    "estimated_runtime_minutes": result.get("estimated_runtime_minutes", 0),
                    "message": f"DAG '{pipeline_name}' created successfully",
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "message": "DAG creation error",
                }

        except Exception as e:
            print(f"❌ Error creating DAG: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Critical error when creating DAG",
            }

    async def create_dag_from_configs(
        self,
        extract_config: ExtractConfig,
        transform_config: TransformConfig | None = None,
        load_config: LoadConfig | None = None,
        pipeline_name: str = "Custom Pipeline",
        owner: str = "data_team",
    ) -> dict[str, Any]:
        """
        Creating DAG from ready Extract/Transform/Load configs.

        Args:
            extract_config: Data extraction configuration
            transform_config: Transformation configuration (optional)
            load_config: Loading configuration (optional)
            pipeline_name: Pipeline name
            owner: Pipeline owner

        Returns:
            Result of DAG creation
        """
        try:
            print(f"🔧 Creating DAG from ready configs: {pipeline_name}")

            # For this method, we will need to extend the DAG system
            # For now, use URL from extract_config
            if extract_config.source_metadata and extract_config.source_metadata.connection_string:
                source_url = (
                    f"{extract_config.source_metadata.source_type}:"
                    f"{extract_config.source_metadata.connection_string}"
                )
                return await self.create_dag_from_url(
                    source_url=source_url, pipeline_name=pipeline_name, owner=owner
                )
            else:
                return {
                    "success": False,
                    "error": "Unable to determine data source from ExtractConfig",
                    "message": "Incorrect extraction configuration",
                }

        except Exception as e:
            print(f"❌ Error creating DAG from configs: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error creating DAG from configurations",
            }

    async def list_generated_dags(self) -> dict[str, Any]:
        """
        Getting list of all generated DAGs.

        Returns:
            List of generated pipelines
        """
        try:
            status = await self.dag_system.get_system_status()

            dags = []
            if self.output_dir.exists():
                for dag_dir in self.output_dir.iterdir():
                    if dag_dir.is_dir() and not dag_dir.name.startswith("."):
                        dag_info = {
                            "pipeline_id": dag_dir.name,
                            "created": dag_dir.stat().st_ctime,
                            "path": str(dag_dir),
                            "has_dag_file": (dag_dir / "airflow" / f"{dag_dir.name}.py").exists(),
                            "has_config": (dag_dir / f"{dag_dir.name}_config.json").exists(),
                        }
                        dags.append(dag_info)

            return {"success": True, "total_dags": len(dags), "dags": dags, "system_status": status}

        except Exception as e:
            return {"success": False, "error": str(e), "dags": []}

    def get_supported_sources(self) -> dict[str, Any]:
        """
        Getting list of supported data source types.

        Returns:
            Information about supported sources
        """
        return {
            "source_types": [
                {
                    "type": "folder",
                    "name": "Local folders",
                    "description": "XML, JSON, CSV files in folders",
                    "example_url": "file://d:/data/xml_files/",
                    "supported_formats": ["xml", "json", "csv"],
                    "ready": True,
                },
                {
                    "type": "postgres",
                    "name": "PostgreSQL",
                    "description": "PostgreSQL databases",
                    "example_url": "postgres://user:pass@localhost:5432/mydb",
                    "supported_formats": ["table"],
                    "ready": True,
                },
                {
                    "type": "clickhouse",
                    "name": "ClickHouse",
                    "description": "ClickHouse analytical DBs",
                    "example_url": "clickhouse://user:pass@localhost:8123/analytics",
                    "supported_formats": ["table"],
                    "ready": False,
                },
                {
                    "type": "kafka",
                    "name": "Apache Kafka",
                    "description": "Streaming data from Kafka",
                    "example_url": "kafka://broker:9092/topic",
                    "supported_formats": ["json"],
                    "ready": False,
                },
                {
                    "type": "s3",
                    "name": "Amazon S3",
                    "description": "Object storage S3",
                    "example_url": "s3://bucket/path/",
                    "supported_formats": ["xml", "json", "csv", "parquet"],
                    "ready": False,
                },
                {
                    "type": "api",
                    "name": "REST API",
                    "description": "HTTP API endpoints",
                    "example_url": "https://api.example.com/data",
                    "supported_formats": ["json"],
                    "ready": False,
                },
            ],
            "ready_builders": ["folder", "postgres"],
            "development_builders": ["clickhouse", "kafka", "s3", "api"],
        }


# Synchronous wrappers for convenience
class DAGGeneratorSync:
    """Synchronous wrapper for IntegratedDAGGenerator."""

    def __init__(self, output_dir: str = "generated_dags"):
        """Initialize synchronous generator."""
        self.generator = IntegratedDAGGenerator(output_dir)

    def create_dag(
        self, source_url: str, pipeline_name: str, **kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        """Synchronous DAG creation."""
        return asyncio.run(self.generator.create_dag_from_url(source_url, pipeline_name, **kwargs))

    def list_dags(self) -> dict[str, Any]:
        """Synchronous list of DAGs."""
        return asyncio.run(self.generator.list_generated_dags())


# Export for use in application
__all__ = ["DAGGeneratorSync", "IntegratedDAGGenerator"]
