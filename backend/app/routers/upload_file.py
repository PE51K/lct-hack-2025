"""Router for uploading files to MinIO."""

import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from core.settings import settings

logger = logging.getLogger(__name__)

upload_router = APIRouter()


class UploadFileResponse(BaseModel):
    """Response model for file upload."""

    success: bool
    message: str
    bucket: str | None = None
    file_path: str | None = None
    file_size: int | None = None
    error_message: str | None = None


@upload_router.post("/upload_file")
async def upload_file(
    file: Annotated[UploadFile, File(description="File to upload to MinIO")],
    bucket: Annotated[str, Form(description="Target bucket name")] = None,
    folder: Annotated[str, Form(description="Target folder path")] = "",
) -> UploadFileResponse:
    """
    Upload a file to MinIO S3-compatible storage.

    This endpoint uploads a file to the specified MinIO bucket and folder.
    If no bucket is specified, it uses the default bucket from settings.

    Args:
        file: The file to upload
        bucket: Target bucket name (optional, uses default if not specified)
        folder: Target folder path within the bucket (optional)

    Returns:
        UploadFileResponse with upload status and file information
    """
    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError

        # Use default bucket if not specified
        target_bucket = bucket or settings.s3.bucket_name

        # Construct the file path
        file_path = f"{folder.rstrip('/')}/{file.filename}" if folder else file.filename

        logger.info(
            f"Uploading file {file.filename} to bucket {target_bucket} at path {file_path}"
        )

        # Create S3 client
        s3_client = boto3.client(
            "s3",
            endpoint_url=settings.s3.endpoint_url,
            aws_access_key_id=settings.s3.access_key_id,
            aws_secret_access_key=settings.s3.secret_access_key,
            region_name=settings.s3.region,
        )

        # Ensure bucket exists
        try:
            s3_client.head_bucket(Bucket=target_bucket)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                # Bucket doesn't exist, create it
                logger.info(f"Bucket {target_bucket} not found, creating...")
                s3_client.create_bucket(Bucket=target_bucket)
                logger.info(f"Created bucket {target_bucket}")
            else:
                raise

        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Upload to MinIO
        s3_client.put_object(
            Bucket=target_bucket,
            Key=file_path,
            Body=file_content,
            ContentType=file.content_type or "application/octet-stream",
        )

        logger.info(
            f"Successfully uploaded {file.filename} ({file_size} bytes) to {target_bucket}/{file_path}"
        )

        return UploadFileResponse(
            success=True,
            message=f"Файл успешно загружен в MinIO",
            bucket=target_bucket,
            file_path=file_path,
            file_size=file_size,
        )

    except (BotoCoreError, ClientError) as e:
        error_msg = f"MinIO S3 error: {e!s}"
        logger.error(error_msg, exc_info=True)
        return UploadFileResponse(success=False, message="", error_message=error_msg)

    except Exception as e:
        error_msg = f"Unexpected error uploading file: {e!s}"
        logger.error(error_msg, exc_info=True)
        return UploadFileResponse(success=False, message="", error_message=error_msg)
