"""Router for ETL creation (generation) endpoints."""

import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from builders.dag import AirflowFileGenerator, DAGBuilder
from builders.ddl import DDLBuilder
from builders.extract import ExtractConfigBuilder
from builders.load import LoadConfigBuilder
from builders.transform import TransformConfigBuilder
from models.app import CreateETLRequest, CreateETLResponse

logger = logging.getLogger(__name__)

create_router = APIRouter()


@create_router.post("/create_etl")
async def create_etl(request: CreateETLRequest) -> StreamingResponse:
    """Create an ETL pipeline."""
    logger.info(f"Starting ETL creation for request IDs: {request.ids}")

    # Define async streaming generator
    async def create(request: CreateETLRequest) -> AsyncGenerator[str, None]:
        try:
            logger.info("Initializing ETL creation process")
            # Step 1. Build ExtractConfig from user prompt (20%)
            logger.info("Step 1: Building extract configuration")
            yield (
                CreateETLResponse(
                    ids=request.ids,
                    processing_done=False,
                    processing_percentage_done=20.0,
                    processing_message="Building extract configuration...",
                    success=True,
                ).model_dump_json()
                + "\n"
            )

            extract_config = await ExtractConfigBuilder.from_user_prompt(request.user_prompt)
            logger.info(f"ExtractConfig received: {extract_config}")

            # Step 3. Generate LoadConfig from ExtractConfig and user prompt (40%)
            yield (
                CreateETLResponse(
                    ids=request.ids,
                    processing_done=False,
                    processing_percentage_done=40.0,
                    processing_message="Generating load configuration with AI...",
                    success=True,
                ).model_dump_json()
                + "\n"
            )

            load_builder = LoadConfigBuilder()
            load_config = await load_builder(extract_config, request.user_prompt)
            logger.info(f"LoadConfig received: {load_config}")

            # Step 4. Generate DDL from ExtractConfig and LoadConfig (60%)
            yield (
                CreateETLResponse(
                    ids=request.ids,
                    processing_done=False,
                    processing_percentage_done=60.0,
                    processing_message="Generating DDL...",
                    success=True,
                ).model_dump_json()
                + "\n"
            )

            ddl_builder = DDLBuilder()
            ddl = await ddl_builder(extract_config, load_config)
            logger.info(f"DDL received: {ddl}")

            # Step 5. Generate TransformConfig from DDL and user prompt (80%)
            yield (
                CreateETLResponse(
                    ids=request.ids,
                    processing_done=False,
                    processing_percentage_done=80.0,
                    processing_message="Generating transformation configuration with AI...",
                    success=True,
                ).model_dump_json()
                + "\n"
            )

            transform_builder = TransformConfigBuilder()
            transform_config = await transform_builder(
                ddl, extract_config, load_config, request.user_prompt
            )
            logger.info(f"TransformConfig received: {transform_config}")

            # Step 6. Generate DAG model from all configs (90%)
            yield (
                CreateETLResponse(
                    ids=request.ids,
                    processing_done=False,
                    processing_percentage_done=90.0,
                    processing_message="Generating DAG configuration...",
                    success=True,
                ).model_dump_json()
                + "\n"
            )

            dag_builder = DAGBuilder()
            dag = await dag_builder(extract_config, transform_config, load_config, ddl)
            logger.info(f"DAG model created: {dag.dag_id}")

            # Step 7. Generate Airflow DAG files (95%)
            yield (
                CreateETLResponse(
                    ids=request.ids,
                    processing_done=False,
                    processing_percentage_done=95.0,
                    processing_message="Generating Airflow DAG files...",
                    success=True,
                ).model_dump_json()
                + "\n"
            )

            # Generate executable Airflow files
            file_generator = AirflowFileGenerator()
            generated_files = await file_generator.generate_dag_files(
                dag=dag,
                extract_config=extract_config,
                transform_config=transform_config,
                load_config=load_config,
                ddl=ddl,
                user_id=request.ids.user_id,
                thread_id=request.ids.thread_id,
            )

            # Update DAG with generated file paths
            dag.generated_files = generated_files
            dag.dag_file_path = generated_files.get("dag_file")
            
            logger.info(f"Generated {len(generated_files)} Airflow files")
            logger.info(f"DAG file: {dag.dag_file_path}")

            # Final response with all artefacts
            yield (
                CreateETLResponse(
                    ids=request.ids,
                    processing_done=True,
                    processing_percentage_done=100.0,
                    processing_message="ETL creation completed successfully! Airflow DAG files generated.",
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
            logger.error(f"Error during ETL creation: {e}", exc_info=True)
            yield (
                CreateETLResponse(
                    ids=request.ids,
                    processing_done=True,
                    processing_percentage_done=0.0,
                    processing_message=f"Error during ETL creation: {e!s}",
                    success=False,
                    error_message=str(e),
                ).model_dump_json()
                + "\n"
            )

    return StreamingResponse(create(request), media_type="application/x-ndjson")
