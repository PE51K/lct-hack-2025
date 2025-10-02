"""Router for ETL update endpoints."""

import asyncio
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from builders.dag import DAGBuilder
from builders.ddl import DDLBuilder
from builders.extract import ExtractConfigBuilder
from builders.load import LoadConfigBuilder
from builders.transform import TransformConfigBuilder
from models.app.update_etl import UpdateETLRequest, UpdateETLResponse

logger = logging.getLogger(__name__)

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

    async def publish(request: UpdateETLRequest) -> AsyncGenerator[str, None]:
        try:
            # Step 1: Processing feedback (10%)
            yield (
                UpdateETLResponse(
                    ids=ids,
                    processing_done=False,
                    processing_percentage_done=10.0,
                    processing_message="Processing user feedback...",
                    success=True,
                ).model_dump_json()
                + "\n"
            )
            await asyncio.sleep(1)

            # For update, we refine existing configs based on feedback
            feedback_text = " ".join(
                [f"{item.area}: {item.message}" for item in request.feedback.items]
            )
            if request.feedback.overall:
                feedback_text += f" Overall: {request.feedback.overall}"

            # Step 2: Updating extract config (30%)
            yield (
                UpdateETLResponse(
                    ids=ids,
                    processing_done=False,
                    processing_percentage_done=30.0,
                    processing_message="Updating extract configuration based on feedback...",
                    success=True,
                ).model_dump_json()
                + "\n"
            )

            extract_feedback = [item for item in request.feedback.items if item.area == "extract"]
            extract_config = await ExtractConfigBuilder.from_user_prompt(
                feedback_text, request.extract_config, extract_feedback, request.feedback.overall
            )

            # Step 3: Updating load config (50%)
            yield (
                UpdateETLResponse(
                    ids=ids,
                    processing_done=False,
                    processing_percentage_done=50.0,
                    processing_message="Updating load configuration...",
                    success=True,
                ).model_dump_json()
                + "\n"
            )

            load_builder = LoadConfigBuilder()
            load_feedback = [item for item in request.feedback.items if item.area == "load"]
            load_config = await load_builder(
                extract_config,
                feedback_text,
                request.load_config,
                load_feedback,
                request.feedback.overall,
            )

            # Step 4: Updating DDL (70%)
            yield (
                UpdateETLResponse(
                    ids=ids,
                    processing_done=False,
                    processing_percentage_done=70.0,
                    processing_message="Updating DDL statements...",
                    success=True,
                ).model_dump_json()
                + "\n"
            )

            ddl_builder = DDLBuilder()
            ddl = await ddl_builder(extract_config, load_config)

            # Step 5: Updating transform config (90%)
            yield (
                UpdateETLResponse(
                    ids=ids,
                    processing_done=False,
                    processing_percentage_done=90.0,
                    processing_message="Updating transform configuration...",
                    success=True,
                ).model_dump_json()
                + "\n"
            )

            transform_builder = TransformConfigBuilder()
            transform_feedback = [
                item for item in request.feedback.items if item.area == "transform"
            ]
            transform_config = await transform_builder(
                ddl,
                extract_config,
                load_config,
                feedback_text,
                request.transform_config,
                transform_feedback,
                request.feedback.overall,
            )

            # Step 6: Updating DAG (100%)
            yield (
                UpdateETLResponse(
                    ids=ids,
                    processing_done=False,
                    processing_percentage_done=100.0,
                    processing_message="Updating DAG structure...",
                    success=True,
                ).model_dump_json()
                + "\n"
            )

            dag_builder = DAGBuilder()
            dag = await dag_builder(extract_config, transform_config, load_config, ddl)

            # Final: Complete
            yield (
                UpdateETLResponse(
                    ids=ids,
                    processing_done=True,
                    processing_percentage_done=100.0,
                    processing_message="ETL update complete.",
                    success=True,
                    extract_config=extract_config,
                    transform_config=transform_config,
                    load_config=load_config,
                    ddl=ddl,
                    dag=dag,
                ).model_dump_json()
                + "\n"
            )

        except Exception as e:
            yield (
                UpdateETLResponse(
                    ids=ids,
                    processing_done=True,
                    processing_percentage_done=0.0,
                    processing_message=f"Error during ETL update: {e!s}",
                    success=False,
                    error_message=str(e),
                ).model_dump_json()
                + "\n"
            )

    return StreamingResponse(publish(request), media_type="application/x-ndjson")
