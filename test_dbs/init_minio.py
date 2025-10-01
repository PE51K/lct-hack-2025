#!/usr/bin/env python3
"""
Test databases initialization script.

Connects to test databases (PostgreSQL, ClickHouse, MinIO) and inserts test data.
"""

import sys
from pathlib import Path

import boto3

from core import logger, settings


def init_minio() -> None:
    """Initialize MinIO with test data files."""
    logger.info("Initializing MinIO...")

    # Use environment variables if available (for Docker), otherwise use settings
    endpoint_url = f"http://{settings.minio.host}:{settings.minio.port}"

    try:
        # Create S3 client for MinIO
        s3_client = boto3.client(
            "s3",
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
    """Main function to initialize MinIO test data."""
    logger.info("Starting MinIO initialization...")

    try:
        init_minio()
        logger.info("MinIO initialized successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize MinIO: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
