"""Router for ETL update endpoints."""

import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from models.update_etl import UpdateETLRequest, UpdateETLResponse

from ..mock_data import (
    generate_mock_dag,
    generate_mock_ddl,
    generate_mock_extract_config,
    generate_mock_load_config,
    generate_mock_transform_config,
)

router = APIRouter()

@router.post("/update_etl")
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