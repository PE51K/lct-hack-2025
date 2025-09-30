"""Router for ETL update endpoints."""

import asyncio
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ai.workflows.build_load_config import build_load_config_from_extract_config_and_prompt
from ai.workflows.build_transform_config import build_transform_config_from_configs_and_prompt
from ai.workflows.extract_source import extract_source_from_user_prompt
from builders.dag import generate_dag_from_configs
from builders.ddl import generate_ddl_from_configs
from builders.extract import ExtractConfigBuilder
from models.app.update_etl import UpdateETLRequest, UpdateETLResponse

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

            # For update, we start with existing configs and modify based on feedback
            # For simplicity, we'll regenerate from scratch with feedback incorporated into prompt
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

            # Re-extract source with feedback
            source = await extract_source_from_user_prompt(feedback_text)
            extract_config = await ExtractConfigBuilder.from_source(source)

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

            load_config = await build_load_config_from_extract_config_and_prompt(
                extract_config, feedback_text
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

            ddl = await generate_ddl_from_configs(extract_config, load_config)

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

            transform_config = await build_transform_config_from_configs_and_prompt(
                ddl, extract_config, load_config, feedback_text
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

            dag = await generate_dag_from_configs(
                extract_config, transform_config, load_config, ddl
            )

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
