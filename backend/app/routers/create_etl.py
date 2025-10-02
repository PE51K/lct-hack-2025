"""Router for ETL creation (generation) endpoints."""

import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from builders.ddl import DDLBuilder
from builders.extract import ExtractConfigBuilder
from builders.load import LoadConfigBuilder
from builders.transform import TransformConfigBuilder
from models.app import CreateETLRequest, CreateETLResponse, CredentialField, CredentialsRequired

logger = logging.getLogger(__name__)

create_router = APIRouter()


def _generate_credentials_form(target_type: str) -> CredentialsRequired:
    """Generate credentials form based on target DB type."""
    if target_type == "postgres":
        return CredentialsRequired(
            target_type="postgres",
            fields=[
                CredentialField(
                    name="host",
                    label="PostgreSQL Host",
                    type="text",
                    placeholder="localhost",
                    required=True,
                ),
                CredentialField(
                    name="port",
                    label="Port",
                    type="number",
                    placeholder="5432",
                    default=5432,
                    required=True,
                ),
                CredentialField(
                    name="username",
                    label="Username",
                    type="text",
                    placeholder="postgres",
                    required=True,
                ),
                CredentialField(name="password", label="Password", type="password", required=True),
                CredentialField(
                    name="database",
                    label="Database Name",
                    type="text",
                    placeholder="analytics",
                    required=True,
                ),
                CredentialField(
                    name="schema_name",
                    label="Schema Name",
                    type="text",
                    placeholder="public",
                    default="public",
                    required=False,
                ),
                CredentialField(
                    name="table_name",
                    label="Table Name (Optional Override)",
                    type="text",
                    placeholder="Leave empty to use AI-generated table name",
                    required=False,
                ),
            ],
        )
    elif target_type == "clickhouse":
        return CredentialsRequired(
            target_type="clickhouse",
            fields=[
                CredentialField(
                    name="host",
                    label="ClickHouse Host",
                    type="text",
                    placeholder="localhost",
                    required=True,
                ),
                CredentialField(
                    name="port",
                    label="HTTP Port",
                    type="number",
                    placeholder="8123",
                    default=8123,
                    required=True,
                ),
                CredentialField(
                    name="username",
                    label="Username",
                    type="text",
                    placeholder="default",
                    required=True,
                ),
                CredentialField(name="password", label="Password", type="password", required=False),
                CredentialField(
                    name="database",
                    label="Database Name",
                    type="text",
                    placeholder="default",
                    required=True,
                ),
                CredentialField(
                    name="table_name",
                    label="Table Name (Optional Override)",
                    type="text",
                    placeholder="Leave empty to use AI-generated table name",
                    required=False,
                ),
            ],
        )
    elif target_type == "hdfs":
        return CredentialsRequired(
            target_type="hdfs",
            fields=[
                CredentialField(
                    name="namenode_host",
                    label="HDFS NameNode Host",
                    type="text",
                    placeholder="namenode.example.com",
                    required=True,
                ),
                CredentialField(
                    name="namenode_port",
                    label="NameNode Port",
                    type="number",
                    placeholder="9870",
                    default=9870,
                    required=True,
                ),
                CredentialField(
                    name="user",
                    label="HDFS User",
                    type="text",
                    placeholder="hdfs",
                    required=True,
                ),
                CredentialField(
                    name="base_path",
                    label="Base HDFS Path",
                    type="text",
                    placeholder="/data/etl",
                    required=True,
                ),
                CredentialField(
                    name="authentication",
                    label="Authentication Method",
                    type="text",
                    placeholder="simple",
                    default="simple",
                    required=False,
                ),
                CredentialField(
                    name="table_name",
                    label="Target File/Directory Name (Optional Override)",
                    type="text",
                    placeholder="Leave empty to use AI-generated name",
                    required=False,
                ),
            ],
        )
    else:
        # For unknown types, provide generic fields
        return CredentialsRequired(
            target_type=target_type,
            fields=[
                CredentialField(
                    name="connection_string",
                    label="Connection String",
                    type="text",
                    placeholder=f"{target_type}://host:port",
                    required=True,
                )
            ],
        )


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

            # STOP HERE - Don't create DAG yet
            # Step 6. Generate credentials form (85%)
            yield (
                CreateETLResponse(
                    ids=request.ids,
                    processing_done=False,
                    processing_percentage_done=85.0,
                    processing_message="Preparing credentials form...",
                    success=True,
                ).model_dump_json()
                + "\n"
            )

            # Generate credentials form based on AI recommendation
            credentials_required = _generate_credentials_form(
                load_config.target_storage_type.storage_type
            )

            logger.info(
                f"AI recommended target: {load_config.target_storage_type.storage_type} - "
                f"{load_config.target_storage_type.explanation}"
            )

            # Final response with configs and credentials form (NO DAG yet)
            # Frontend will store configs and send them back with credentials
            yield (
                CreateETLResponse(
                    ids=request.ids,
                    processing_done=True,
                    processing_percentage_done=80.0,  # Not 100% - stopped before DAG
                    processing_message="Configuration complete. Please provide target database "
                    "credentials.",
                    success=True,
                    extract_config=extract_config,
                    transform_config=transform_config,
                    load_config=load_config,
                    ddl=ddl,
                    dag=None,  # No DAG yet!
                    credentials_required=credentials_required,  # NEW: Credentials form
                    next_step="create_dag",  # NEW: Tell frontend what's next
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
