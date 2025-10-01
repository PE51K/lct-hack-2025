#!/usr/bin/env python3
"""
Test databases initialization script.

Connects to test databases (PostgreSQL, ClickHouse, MinIO) and inserts test data.
"""

import os
import sys
from pathlib import Path
from typing import List

import boto3
import psycopg2
from clickhouse_driver import Client

from core import logger, settings


def init_postgres() -> None:
    """Initialize PostgreSQL with test data."""
    logger.info("Initializing PostgreSQL...")

    try:
        conn = psycopg2.connect(settings.postgres.connection_string)
        conn.autocommit = True
        cursor = conn.cursor()

        # Read and execute SQL file
        sql_file = Path(__file__).parent / "test_data" / "postgres" / "init.sql"
        with open(sql_file, "r") as f:
            sql = f.read()

        cursor.execute(sql)
        logger.info("PostgreSQL test data inserted successfully")

    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()


def init_clickhouse() -> None:
    """Initialize ClickHouse with test data."""
    logger.info("Initializing ClickHouse...")

    try:
        client = Client(
            host=settings.clickhouse.host,
            port=settings.clickhouse.port,
            user=settings.clickhouse.user,
            password=settings.clickhouse.password,
        )

        # Read and execute SQL file
        sql_file = Path(__file__).parent / "test_data" / "clickhouse" / "init.sql"
        with open(sql_file, "r") as f:
            sql = f.read()

        # Split SQL into individual statements
        statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]

        for statement in statements:
            if statement:
                client.execute(statement)

        logger.info("ClickHouse test data inserted successfully")

    except Exception as e:
        logger.error(f"Failed to initialize ClickHouse: {e}")
        raise


def init_minio() -> None:
    """Initialize MinIO with test data files."""
    logger.info("Initializing MinIO...")

    # Use environment variables if available (for Docker), otherwise use settings
    minio_host = os.getenv('TEST_MINIO_HOST', settings.minio.host)
    endpoint_url = f"http://{minio_host}:{settings.minio.port}"

    try:
        # Create S3 client for MinIO
        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=settings.minio.root_user,
            aws_secret_access_key=settings.minio.root_password,
        )

        # Create bucket if it doesn't exist
        try:
            s3_client.create_bucket(Bucket=settings.minio.bucket_name)
            logger.info(f"Created bucket: {settings.minio.bucket_name}")
        except s3_client.exceptions.BucketAlreadyExists:
            logger.info(f"Bucket {settings.minio.bucket_name} already exists")
        except s3_client.exceptions.BucketAlreadyOwnedByYou:
            logger.info(f"Bucket {settings.minio.bucket_name} already owned by you")

        # Upload test files
        test_data_dir = Path(__file__).parent / "test_data" / "s3"
        for file_path in test_data_dir.rglob("*"):
            if file_path.is_file():
                # Create key path relative to test_data/s3
                key = str(file_path.relative_to(test_data_dir))

                with open(file_path, "rb") as f:
                    s3_client.put_object(
                        Bucket=settings.minio.bucket_name,
                        Key=key,
                        Body=f,
                    )
                logger.info(f"Uploaded {key} to MinIO")

        logger.info("MinIO test data uploaded successfully")

    except Exception as e:
        logger.error(f"Failed to initialize MinIO: {e}")
        raise


def main() -> None:
    """Main function to initialize all test databases."""
    logger.info("Starting test databases initialization...")

    try:
        init_postgres()
        init_clickhouse()
        init_minio()
        logger.info("All test databases initialized successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize test databases: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()