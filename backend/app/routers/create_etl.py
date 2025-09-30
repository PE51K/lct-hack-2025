"""Router for ETL creation (generation) endpoints."""

import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from models.generate_etl import GenerateETLRequest, GenerateETLResponse

from ..mock_data import (
    generate_mock_dag,
    generate_mock_ddl,
    generate_mock_extract_config,
    generate_mock_load_config,
    generate_mock_transform_config,
)

router = APIRouter()

@router.post("/generate_etl")
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