"""Router for fetching sample data from target database."""

import logging
from typing import Any

import psycopg2
from fastapi import APIRouter
from psycopg2.extensions import quote_ident
from pydantic import BaseModel

logger = logging.getLogger(__name__)

fetch_sample_router = APIRouter()


class FetchSampleRequest(BaseModel):
    """Request model for fetching sample data."""

    host: str
    port: int
    database: str
    username: str
    password: str
    schema: str = "public"
    table: str
    limit: int = 10


class FetchSampleResponse(BaseModel):
    """Response model for sample data."""

    success: bool
    columns: list[str] = []
    rows: list[dict[str, Any]] = []
    total_rows: int = 0
    error_message: str | None = None


@fetch_sample_router.post("/fetch_sample")
async def fetch_sample(request: FetchSampleRequest) -> FetchSampleResponse:
    """
    Fetch sample data from the target PostgreSQL database.

    This endpoint connects to the specified database and retrieves
    a sample of rows from the specified table.

    Args:
        request: FetchSampleRequest with database credentials and table info

    Returns:
        FetchSampleResponse with sample data or error message
    """
    connection = None
    cursor = None

    try:
        # Build connection string
        connection_string = (
            f"host={request.host} "
            f"port={request.port} "
            f"dbname={request.database} "
            f"user={request.username} "
            f"password={request.password}"
        )

        logger.info(
            f"Connecting to database: {request.username}@{request.host}:{request.port}/"
            f"{request.database}"
        )

        # Connect to the database
        connection = psycopg2.connect(connection_string)
        cursor = connection.cursor()

        # Get total row count
        schema_quoted = quote_ident(request.schema, connection)
        table_quoted = quote_ident(request.table, connection)
        count_query = f"SELECT COUNT(*) FROM {schema_quoted}.{table_quoted}"  # noqa: S608
        cursor.execute(count_query)
        total_rows = cursor.fetchone()[0]

        logger.info(f"Total rows in {request.schema}.{request.table}: {total_rows}")

        # Fetch sample data
        sample_query = f"SELECT * FROM {schema_quoted}.{table_quoted} LIMIT %s"  # noqa: S608
        cursor.execute(sample_query, (request.limit,))

        # Get column names
        columns = [desc[0] for desc in cursor.description]

        # Fetch rows and convert to list of dicts
        rows = []
        for row in cursor.fetchall():
            row_dict = {}
            for i, value in enumerate(row):
                # Convert values to JSON-serializable types
                if value is not None:
                    row_dict[columns[i]] = str(value)
                else:
                    row_dict[columns[i]] = None
            rows.append(row_dict)

        logger.info(f"Successfully fetched {len(rows)} sample rows")

        return FetchSampleResponse(success=True, columns=columns, rows=rows, total_rows=total_rows)

    except psycopg2.OperationalError as e:
        error_msg = f"Could not connect to database: {e!s}"
        logger.error(error_msg)
        return FetchSampleResponse(success=False, error_message=error_msg)

    except psycopg2.ProgrammingError as e:
        error_msg = f"Database query error (table might not exist yet): {e!s}"
        logger.error(error_msg)
        return FetchSampleResponse(success=False, error_message=error_msg)

    except Exception as e:
        error_msg = f"Unexpected error fetching sample data: {e!s}"
        logger.error(error_msg, exc_info=True)
        return FetchSampleResponse(success=False, error_message=error_msg)

    finally:
        # Clean up connections
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            logger.info("Database connection closed")
