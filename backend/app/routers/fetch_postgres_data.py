"""Fetch data from PostgreSQL table for visualization."""

import logging
from typing import Any

import psycopg2
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class FetchPostgresDataRequest(BaseModel):
    """Request to fetch PostgreSQL data."""

    host: str
    port: int
    database: str
    username: str
    password: str
    schema: str = "public"
    table: str
    limit: int = 100


class FetchPostgresDataResponse(BaseModel):
    """Response with PostgreSQL data."""

    success: bool
    columns: list[dict[str, str]]  # [{"name": "id", "type": "integer"}, ...]
    rows: list[dict[str, Any]]  # [{"id": 1, "name": "John"}, ...]
    total_rows: int
    error_message: str | None = None


@router.post("/fetch_postgres_data", response_model=FetchPostgresDataResponse)
async def fetch_postgres_data(request: FetchPostgresDataRequest) -> FetchPostgresDataResponse:
    """
    Fetch data from PostgreSQL table.

    Args:
        request: PostgreSQL connection details and table name

    Returns:
        FetchPostgresDataResponse with table data
    """
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=request.host,
            port=request.port,
            database=request.database,
            user=request.username,
            password=request.password,
        )
        cursor = conn.cursor()

        # Get column information
        cursor.execute(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
            """,
            (request.schema, request.table),
        )
        column_info = cursor.fetchall()

        if not column_info:
            return FetchPostgresDataResponse(
                success=False,
                columns=[],
                rows=[],
                total_rows=0,
                error_message=f"Table {request.schema}.{request.table} not found",
            )

        columns = [{"name": col[0], "type": col[1]} for col in column_info]

        # Get total row count
        cursor.execute(f'SELECT COUNT(*) FROM "{request.schema}"."{request.table}"')
        total_rows = cursor.fetchone()[0]

        # Fetch data with limit
        column_names = [col["name"] for col in columns]
        columns_str = ", ".join(f'"{col}"' for col in column_names)
        cursor.execute(
            f'SELECT {columns_str} '
            f'FROM "{request.schema}"."{request.table}" LIMIT %s',
            (request.limit,),
        )
        rows_data = cursor.fetchall()

        # Convert rows to dict format
        rows = []
        for row in rows_data:
            row_dict = {}
            for i, col_name in enumerate(column_names):
                # Convert values to JSON-serializable types
                value = row[i]
                if value is not None:
                    # Convert to string for dates, decimals, etc.
                    row_dict[col_name] = str(value) if not isinstance(value, (str, int, float, bool)) else value
                else:
                    row_dict[col_name] = None
            rows.append(row_dict)

        cursor.close()
        conn.close()

        logger.info(
            f"Successfully fetched {len(rows)} rows from {request.schema}.{request.table}"
        )

        return FetchPostgresDataResponse(
            success=True,
            columns=columns,
            rows=rows,
            total_rows=total_rows,
        )

    except psycopg2.Error as e:
        logger.error(f"PostgreSQL error: {e}")
        return FetchPostgresDataResponse(
            success=False,
            columns=[],
            rows=[],
            total_rows=0,
            error_message=f"Database error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error fetching PostgreSQL data: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
