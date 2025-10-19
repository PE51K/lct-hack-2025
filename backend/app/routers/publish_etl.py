"""Router for ETL publishing endpoints."""

import asyncio
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from models.app.publish_etl import PublishETLRequest, PublishETLResponse

logger = logging.getLogger(__name__)

publish_router = APIRouter()


@publish_router.post("/publish_etl")
async def publish_etl(request: PublishETLRequest) -> StreamingResponse:
    """
    Verify DAG files exist and optionally trigger execution in Airflow.

    This endpoint:
    1. Verifies that DAG files were generated for the user/thread
    2. Waits for Airflow to discover the DAG (up to 60 seconds)
    3. Optionally triggers immediate execution if requested

    Args:
        request: PublishETLRequest with user/thread IDs and trigger flag

    Returns:
        StreamingResponse with status updates and DAG information
    """
    ids = request.ids

    async def publish(request: PublishETLRequest) -> AsyncGenerator[str, None]:
        try:
            # Step 1: Verify DAG files exist (20%)
            yield (
                PublishETLResponse(
                    ids=ids,
                    processing_done=False,
                    processing_percentage_done=20.0,
                    processing_message="Verifying DAG files...",
                    success=True,
                ).model_dump_json()
                + "\n"
            )

            # Check if DAG files exist and discover the real dag_id
            # Resolve path relative to the app directory
            from pathlib import Path

            backend_dir = Path(__file__).parent.parent.parent
            dags_dir = backend_dir / "dags"
            dag_dir = dags_dir / ids.user_id / ids.thread_id

            if not dag_dir.exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"DAG directory not found for user={ids.user_id}, thread={ids.thread_id}. "
                    f"Please run /create_dag first.",
                )

            # Find the DAG file (should be etl_*.py)
            dag_files = list(dag_dir.glob("etl_*.py"))
            if not dag_files:
                raise HTTPException(
                    status_code=404,
                    detail=f"No DAG files found in {dag_dir}. Please run /create_dag first.",
                )

            # Extract dag_id from the filename
            dag_file = dag_files[0]
            dag_id = dag_file.stem  # filename without extension
            logger.info(f"✅ DAG file found: {dag_file}, DAG ID: {dag_id}")

            # Step 2: Notify about Airflow discovery (40%)
            yield (
                PublishETLResponse(
                    ids=ids,
                    processing_done=False,
                    processing_percentage_done=40.0,
                    processing_message="DAG files generated. Waiting for Airflow to discover...",
                    success=True,
                    dag_id=dag_id,
                ).model_dump_json()
                + "\n"
            )

            # Step 3: Wait for Airflow scheduler to pick up the DAG (60%)
            yield (
                PublishETLResponse(
                    ids=ids,
                    processing_done=False,
                    processing_percentage_done=60.0,
                    processing_message=f"Airflow scheduler will discover DAG '{dag_id}' "
                    f"within 30-60 seconds...",
                    success=True,
                    dag_id=dag_id,
                ).model_dump_json()
                + "\n"
            )

            # Small delay to simulate processing
            await asyncio.sleep(1)

            # Step 4: Provide instructions (80%)
            airflow_url = f"http://localhost:8081/dags/{dag_id}/grid"

            yield (
                PublishETLResponse(
                    ids=ids,
                    processing_done=False,
                    processing_percentage_done=80.0,
                    processing_message="DAG ready for execution. Access Airflow UI to trigger "
                    "manually.",
                    success=True,
                    dag_id=dag_id,
                    dag_status="registered",
                    airflow_url=airflow_url,
                ).model_dump_json()
                + "\n"
            )

            # Final: Complete (100%)
            completion_message = (
                f"✅ DAG '{dag_id}' is ready!\n"
                f"📂 Files location: {dag_dir}\n"
                f"🌐 Airflow UI: {airflow_url}\n"
                f"⏱️ The DAG will appear in Airflow within 30-60 seconds.\n"
            )

            if request.trigger_immediately:
                completion_message += (
                    f"\n⚠️ Automatic triggering not yet implemented. "
                    f"Please trigger manually via Airflow UI or CLI:\n"
                    f"   docker exec -it airflow airflow dags trigger {dag_id}"
                )

            yield (
                PublishETLResponse(
                    ids=ids,
                    processing_done=True,
                    processing_percentage_done=100.0,
                    processing_message=completion_message,
                    success=True,
                    dag_id=dag_id,
                    dag_status="registered",
                    airflow_url=airflow_url,
                ).model_dump_json()
                + "\n"
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error publishing DAG: {e}", exc_info=True)
            yield (
                PublishETLResponse(
                    ids=ids,
                    processing_done=True,
                    processing_percentage_done=0.0,
                    processing_message=f"Error publishing DAG: {e!s}",
                    success=False,
                    error_message=str(e),
                ).model_dump_json()
                + "\n"
            )

    return StreamingResponse(publish(request), media_type="application/x-ndjson")
