"""Router for ETL publishing endpoints."""

import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from models.app.publish_etl import PublishETLRequest, PublishETLResponse

publish_router = APIRouter()


@publish_router.post("/publish_etl")
async def publish_etl(request: PublishETLRequest) -> StreamingResponse:
    """
    Publishes the ETL pipeline to Airflow.

    Args:
        request (PublishETLRequest): The request containing metadata.

    Returns:
        StreamingResponse: A streaming response with publishing status updates.
    """
    ids = request.ids

    async def publish(request: PublishETLRequest) -> PublishETLResponse:
        # Step 1: Starting publishing
        yield (
            json.dumps(
                PublishETLResponse(
                    ids=ids,
                    processing_done=False,
                    processing_percentage_done=25.0,
                    processing_message="Starting ETL publishing...",
                    success=True,
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 2: Send Airflow command to create storage
        yield (
            json.dumps(
                PublishETLResponse(
                    ids=ids,
                    processing_done=False,
                    processing_percentage_done=50.0,
                    processing_message="Sending Airflow command to create storage...",
                    success=True,
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(2)

        # Step 3: Send ETL DAG to Airflow
        yield (
            json.dumps(
                PublishETLResponse(
                    ids=ids,
                    processing_done=False,
                    processing_percentage_done=75.0,
                    processing_message="Sending ETL DAG to Airflow...",
                    success=True,
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(2)

        # Final: Complete
        yield (
            json.dumps(
                PublishETLResponse(
                    ids=ids,
                    processing_done=True,
                    processing_percentage_done=100.0,
                    processing_message="ETL publishing completed successfully.",
                    success=True,
                ).model_dump()
            )
            + "\n"
        )

    return StreamingResponse(publish(request), media_type="application/x-ndjson")

