"""Router for DAG file generation after credentials provided."""

import logging

from fastapi import APIRouter, HTTPException

from builders.dag import AirflowFileGenerator, DAGBuilder
from builders.ddl import DDLBuilder
from models.app import CreateDAGRequest, CreateDAGResponse
from models.app.create_dag import ClickHouseCredentials, HDFSCredentials, PostgresCredentials
from models.extract import ExtractConfig
from models.load import LoadConfig
from models.transform import TransformConfig

logger = logging.getLogger(__name__)

create_dag_router = APIRouter()


@create_dag_router.post("/create_dag")
async def create_dag(request: CreateDAGRequest) -> CreateDAGResponse:
    """
    Create DAG files after user provides target credentials.

    This endpoint is called after /create_etl when user provides credentials.
    It loads the saved configs, updates with credentials, and creates DAG files.
    """
    try:
        logger.info(f"Creating DAG for user={request.ids.user_id}, thread={request.ids.thread_id}")

        # 1. Parse configs from request (sent by frontend)
        extract_config = ExtractConfig(**request.extract_config)
        transform_config = TransformConfig(**request.transform_config)
        load_config = LoadConfig(**request.load_config)

        logger.info(f"Processing target type: {load_config.target_storage_type.storage_type}")

        # 2. Update LoadConfig with real credentials
        updated_load_config = _update_connection_string(load_config, request.target_credentials)

        logger.info(
            f"Updated connection string (masked): "
            f"{_mask_credentials(updated_load_config.target_storage_connection_string)}"
        )

        # 3. Always regenerate DDL to ensure table name matches load_config
        # This handles cases where the DDL was created with a different table name
        logger.info(f"Regenerating DDL for table: {updated_load_config.table_name}")
        ddl_builder = DDLBuilder()
        updated_ddl = await ddl_builder(extract_config, updated_load_config)
        logger.info("DDL regenerated successfully")

        # 4. Create DAG model
        dag_builder = DAGBuilder()
        dag = await dag_builder(extract_config, transform_config, updated_load_config, updated_ddl)

        logger.info(f"DAG model created: {dag.dag_id}")

        # 4. Generate DAG files
        file_generator = AirflowFileGenerator()
        generated_files = await file_generator.generate_dag_files(
            dag=dag,
            extract_config=extract_config,
            transform_config=transform_config,
            load_config=updated_load_config,
            ddl=updated_ddl,
            user_id=request.ids.user_id,
            thread_id=request.ids.thread_id,
        )

        dag.generated_files = generated_files
        dag.dag_file_path = generated_files.get("dag_file")

        logger.info(f"Generated {len(generated_files)} DAG files")
        logger.info("DAG creation completed successfully")

        return CreateDAGResponse(
            ids=request.ids,
            processing_done=True,
            processing_percentage_done=100.0,
            processing_message="DAG created successfully!",
            success=True,
            dag=dag,
            updated_load_config=updated_load_config,
            updated_ddl=updated_ddl,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating DAG: {e}", exc_info=True)
        return CreateDAGResponse(
            ids=request.ids,
            processing_done=True,
            processing_percentage_done=0.0,
            processing_message=f"Error creating DAG: {e!s}",
            success=False,
            error_message=str(e),
        )


def _update_connection_string(
    load_config: LoadConfig,
    credentials: PostgresCredentials | ClickHouseCredentials | HDFSCredentials,
) -> LoadConfig:
    """Update LoadConfig with user-provided credentials."""
    target_type = load_config.target_storage_type.storage_type

    if target_type == "postgres":
        if not isinstance(credentials, PostgresCredentials):
            raise ValueError(f"Expected PostgresCredentials for target type '{target_type}'")

        connection_string = (
            f"postgresql://{credentials.username}:{credentials.password}"
            f"@{credentials.host}:{credentials.port}/{credentials.database}"
        )
        load_config.database_name = credentials.database
        load_config.schema_name = credentials.schema_name

        # Override table name if provided in credentials
        if credentials.table_name:
            logger.info(
                f"Overriding table name from '{load_config.table_name}' "
                f"to '{credentials.table_name}'"
            )
            load_config.table_name = credentials.table_name

    elif target_type == "clickhouse":
        if not isinstance(credentials, ClickHouseCredentials):
            raise ValueError(f"Expected ClickHouseCredentials for target type '{target_type}'")

        password_part = f":{credentials.password}" if credentials.password else ""
        connection_string = (
            f"clickhouse://{credentials.username}{password_part}"
            f"@{credentials.host}:{credentials.port}/{credentials.database}"
        )
        load_config.database_name = credentials.database

        # Override table name if provided in credentials
        if credentials.table_name:
            logger.info(
                f"Overriding table name from '{load_config.table_name}' "
                f"to '{credentials.table_name}'"
            )
            load_config.table_name = credentials.table_name

    elif target_type == "hdfs":
        if not isinstance(credentials, HDFSCredentials):
            raise ValueError(f"Expected HDFSCredentials for target type '{target_type}'")

        connection_string = (
            f"hdfs://{credentials.namenode_host}:{credentials.namenode_port}{credentials.base_path}"
        )
        # HDFS doesn't have database/schema concept, but we use base_path
        load_config.database_name = credentials.base_path

        # Override table name if provided in credentials
        if credentials.table_name:
            logger.info(
                f"Overriding table name from '{load_config.table_name}' "
                f"to '{credentials.table_name}'"
            )
            load_config.table_name = credentials.table_name

    else:
        raise ValueError(f"Unsupported target storage type: {target_type}")

    # Update config with new connection string
    load_config.target_storage_connection_string = connection_string

    return load_config


def _mask_credentials(connection_string: str) -> str:
    """Mask credentials in connection string for logging."""
    if "://" in connection_string:
        parts = connection_string.split("://")
        if len(parts) == 2 and "@" in parts[1]:
            protocol = parts[0]
            after_at = parts[1].split("@", 1)[1]
            return f"{protocol}://***:***@{after_at}"
    return connection_string
