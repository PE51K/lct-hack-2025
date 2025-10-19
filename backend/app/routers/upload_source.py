"""Router for handling source file uploads."""

import logging
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from builders.extract import ExtractConfigBuilder
from models.app.ids import ThreadUserIds
from models.app.upload_source import UploadSourceResponse

logger = logging.getLogger(__name__)

upload_router = APIRouter()

ALLOWED_EXTENSIONS = {".xml", ".csv", ".json"}
CHUNK_SIZE = 1024 * 1024
HOST_UPLOAD_DIR = Path(__file__).resolve().parents[2] / "volumes" / "user_files"
CONTAINER_UPLOAD_DIR = Path("/opt/airflow/user_files")
HOST_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _sanitize_filename(filename: str) -> str:
    """Return a safe filename without path traversal."""
    return Path(filename).name


@upload_router.post("/upload_source", response_model=UploadSourceResponse)
async def upload_source(
    user_id: str = Form(...),
    thread_id: str = Form(...),
    file: UploadFile = File(...),
) -> UploadSourceResponse:
    """Save uploaded file to a user/thread folder and generate extract config."""
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{extension}'. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    safe_name = _sanitize_filename(file.filename)
    target_dir = HOST_UPLOAD_DIR / user_id / thread_id
    target_dir.mkdir(parents=True, exist_ok=True)

    # Keep a single file inside the directory
    for existing in target_dir.iterdir():
        if existing.is_file():
            existing.unlink()

    target_path = target_dir / safe_name

    logger.info(
        "Storing uploaded file '%s' for user_id=%s thread_id=%s at %s",
        safe_name,
        user_id,
        thread_id,
        target_path,
    )

    with target_path.open("wb") as buffer:
        while True:
            chunk = await file.read(CHUNK_SIZE)
            if not chunk:
                break
            buffer.write(chunk)

    host_source_uri = f"file:{target_dir.as_posix()}"
    container_source_uri = f"file:{(CONTAINER_UPLOAD_DIR / user_id / thread_id).as_posix()}"

    try:
        extract_config = await ExtractConfigBuilder.from_uri(host_source_uri)
        content_metadata = extract_config.content_metadata or []
        content_type = content_metadata[0].content_type if content_metadata else None
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception(
            "Failed to process uploaded file '%s' for user_id=%s thread_id=%s", safe_name, user_id, thread_id
        )
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded file: {exc}") from exc

    # Rewrite connection string for downstream Airflow consumption
    if extract_config.source_metadata:
        extract_config.source_metadata.connection_string = container_source_uri

    return UploadSourceResponse(
        ids=ThreadUserIds(thread_id=thread_id, user_id=user_id),
        filename=safe_name,
        stored_path=str(target_path),
        source_uri=host_source_uri,
        container_source_uri=container_source_uri,
        content_type=content_type,
        extract_config=extract_config,
    )
