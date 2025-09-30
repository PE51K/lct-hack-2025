"""Router for ETL update endpoints."""

import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

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
from models.update_etl import UpdateETLRequest, UpdateETLResponse


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


update_router = APIRouter()


@update_router.post("/update_etl")
async def update_etl(request: UpdateETLRequest) -> StreamingResponse:
    """
    Updates the ETL pipeline based on feedback or error messages.

    Args:
        request (UpdateETLRequest): The request containing feedback and metadata.

    Returns:
        StreamingResponse: A streaming response with update status.
    """
    ids = request.ids

    async def generate():
        # Step 1: Processing feedback
        yield (
            json.dumps(
                UpdateETLResponse(
                    ids=ids,
                    message="Processing user feedback...",
                    done=False,
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 2: Updating extract config
        yield (
            json.dumps(
                UpdateETLResponse(
                    ids=ids,
                    message="Updating extract configuration based on feedback...",
                    done=False,
                    extract_config=generate_mock_extract_config(),
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 3: Updating transform config
        yield (
            json.dumps(
                UpdateETLResponse(
                    ids=ids,
                    message="Updating transform configuration...",
                    done=False,
                    extract_config=generate_mock_extract_config(),
                    transform_config=generate_mock_transform_config(),
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 4: Updating load config
        yield (
            json.dumps(
                UpdateETLResponse(
                    ids=ids,
                    message="Updating load configuration...",
                    done=False,
                    extract_config=generate_mock_extract_config(),
                    transform_config=generate_mock_transform_config(),
                    load_config=generate_mock_load_config(),
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 5: Updating DDL
        yield (
            json.dumps(
                UpdateETLResponse(
                    ids=ids,
                    message="Updating DDL statements...",
                    done=False,
                    extract_config=generate_mock_extract_config(),
                    transform_config=generate_mock_transform_config(),
                    load_config=generate_mock_load_config(),
                    ddl=generate_mock_ddl(),
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 6: Updating DAG
        yield (
            json.dumps(
                UpdateETLResponse(
                    ids=ids,
                    message="Updating DAG structure...",
                    done=False,
                    extract_config=generate_mock_extract_config(),
                    transform_config=generate_mock_transform_config(),
                    load_config=generate_mock_load_config(),
                    ddl=generate_mock_ddl(),
                    dag=generate_mock_dag(),
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Final: Complete
        yield (
            json.dumps(
                UpdateETLResponse(
                    ids=ids,
                    message="ETL update complete.",
                    done=True,
                    extract_config=generate_mock_extract_config(),
                    transform_config=generate_mock_transform_config(),
                    load_config=generate_mock_load_config(),
                    ddl=generate_mock_ddl(),
                    dag=generate_mock_dag(),
                ).model_dump()
            )
            + "\n"
        )

    return StreamingResponse(generate(), media_type="application/x-ndjson")
