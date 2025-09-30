"""Router for ETL execution endpoints."""

import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from models.app.execute_etl import ExecuteETLRequest, ExecuteETLResponse

execute_router = APIRouter()


@execute_router.post("/execute_etl")
async def execute_etl(request: ExecuteETLRequest) -> StreamingResponse:
    """
    Executes the ETL pipeline with provided metadata.

    Args:
        request (ExecuteETLRequest): The request containing metadata.

    Returns:
        StreamingResponse: A streaming response with execution status updates.
    """
    ids = request.ids

    async def generate():
        # Step 1: Starting execution
        yield (
            json.dumps(
                ExecuteETLResponse(
                    ids=ids,
                    message="Starting ETL execution...",
                    done=False,
                    success=False,
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 2: Extract phase
        yield (
            json.dumps(
                ExecuteETLResponse(
                    ids=ids,
                    message="Extracting data from source...",
                    done=False,
                    success=False,
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(2)

        # Step 3: Transform phase
        yield (
            json.dumps(
                ExecuteETLResponse(
                    ids=ids,
                    message="Transforming data...",
                    done=False,
                    success=False,
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(2)

        # Step 4: Load phase
        yield (
            json.dumps(
                ExecuteETLResponse(
                    ids=ids,
                    message="Loading data into target...",
                    done=False,
                    success=False,
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(2)

        # Final: Complete
        yield (
            json.dumps(
                ExecuteETLResponse(
                    ids=ids,
                    message="ETL execution completed successfully.",
                    done=True,
                    success=True,
                ).model_dump()
            )
            + "\n"
        )

    return StreamingResponse(generate(), media_type="application/x-ndjson")
