"""Mock data generators for ETL configurations."""

from models.dag import DAG
from models.ddl import DDL
from models.extract import Content, ContentType, ExtractConfig, Source, SourceType
from models.load import (
    Field,
    FlatMetaModel,
    LoadConfig,
    NestingMetaModel,
    TargetStorageTypeRecommendation,
)
from models.transform import TransformConfig


def generate_mock_extract_config() -> ExtractConfig:
    """Generate mock extract configuration."""
    return ExtractConfig(
        source_metadata=Source(
            source_type=SourceType.folder,
            connection_string="s3://mock-bucket/data/",
            content_type=ContentType.csv,
        ),
        content_metadata=[
            Content(
                message_name="data1.csv",
                metamodel={
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "value": {"type": "number"},
                    },
                },
            )
        ],
        content_statistics={"total_files": 1, "total_size": 1024},
    )


def generate_mock_transform_config() -> TransformConfig:
    """Generate mock transform configuration."""
    return TransformConfig(
        identity_keys=["id"],
        aggregate_keys=["name"],
        versioning_field="timestamp",
    )


def generate_mock_load_config() -> LoadConfig:
    """Generate mock load configuration."""
    return LoadConfig(
        target_storage_type=TargetStorageTypeRecommendation(
            storage_type="postgres",
            explanation="Relational database suitable for structured data.",
        ),
        target_storage_connection_string="postgresql://user:pass@localhost:5432/db",
        nesting_metamodel=NestingMetaModel(
            data_structure={"type": "object"},
            partitioning_key="id",
        ),
        flat_meta_model=FlatMetaModel(
            fields=[
                Field(name="id", data_type="INTEGER", nullable=False),
                Field(name="name", data_type="VARCHAR(255)", nullable=True),
                Field(name="value", data_type="DECIMAL", nullable=True),
            ],
            indexes=[],
            partitioning_key="id",
        ),
    )


def generate_mock_dag() -> DAG:
    """Generate mock DAG."""
    return DAG()  # Empty for now


def generate_mock_ddl() -> DDL:
    """Generate mock DDL."""
    return DDL()  # Empty for now
