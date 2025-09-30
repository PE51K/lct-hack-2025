"""Router for ETL creation (generation) endpoints."""

import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from models.dag import DAG
from models.ddl import DDL
from models.extract import Content, ContentType, ExtractConfig, Source, SourceType
from models.generate_etl import GenerateETLRequest, GenerateETLResponse
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


create_router = APIRouter()


@create_router.post("/generate_etl")
async def create_etl(request: GenerateETLRequest) -> StreamingResponse:
    """
    Generate ETL pipeline and recommendations based on input data URI.

    Args:
        request (GenerateETLRequest): The request containing input data URI and metadata.

    Returns:
        StreamingResponse: A streaming response with generation status updates.
    """
    ids = request.ids

    async def generate():
        # Step 1: Analyzing data
        yield (
            json.dumps(
                GenerateETLResponse(
                    ids=ids,
                    message="Analyzing input data from URI...",
                    done=False,
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 2: Generating extract config
        yield (
            json.dumps(
                GenerateETLResponse(
                    ids=ids,
                    message="Generating extract configuration...",
                    done=False,
                    extract_config=generate_mock_extract_config(),
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 3: Generating transform config
        yield (
            json.dumps(
                GenerateETLResponse(
                    ids=ids,
                    message="Generating transform configuration...",
                    done=False,
                    extract_config=generate_mock_extract_config(),
                    transform_config=generate_mock_transform_config(),
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 4: Generating load config
        yield (
            json.dumps(
                GenerateETLResponse(
                    ids=ids,
                    message="Generating load configuration...",
                    done=False,
                    extract_config=generate_mock_extract_config(),
                    transform_config=generate_mock_transform_config(),
                    load_config=generate_mock_load_config(),
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 5: Generating DDL
        yield (
            json.dumps(
                GenerateETLResponse(
                    ids=ids,
                    message="Generating DDL statements...",
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

        # Step 6: Generating DAG
        yield (
            json.dumps(
                GenerateETLResponse(
                    ids=ids,
                    message="Generating DAG structure...",
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
                GenerateETLResponse(
                    ids=ids,
                    message="ETL generation complete.",
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
