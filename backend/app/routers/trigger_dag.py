"""Trigger DAG execution in Airflow."""

import logging

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class TriggerDAGRequest(BaseModel):
    """Request to trigger DAG execution."""

    dag_id: str


class TriggerDAGResponse(BaseModel):
    """Response from triggering DAG."""

    success: bool
    message: str
    dag_run_id: str | None = None
    error_message: str | None = None


@router.post("/trigger_dag", response_model=TriggerDAGResponse)
async def trigger_dag(request: TriggerDAGRequest) -> TriggerDAGResponse:
    """
    Trigger DAG execution in Airflow.

    Args:
        request: DAG ID to trigger

    Returns:
        TriggerDAGResponse with execution status
    """
    try:
        # Airflow API endpoint
        airflow_url = f"{settings.airflow.url}/api/v1/dags/{request.dag_id}/dagRuns"

        # Prepare request payload
        payload = {
            "conf": {},
        }

        # Make request to Airflow API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                airflow_url,
                json=payload,
                auth=(settings.airflow.username, settings.airflow.password),
                timeout=30.0,
            )

            if response.status_code == 200:
                data = response.json()
                dag_run_id = data.get("dag_run_id", "unknown")

                logger.info(f"Successfully triggered DAG {request.dag_id}, run ID: {dag_run_id}")

                return TriggerDAGResponse(
                    success=True,
                    message=f"DAG {request.dag_id} successfully triggered",
                    dag_run_id=dag_run_id,
                )
            else:
                error_msg = f"Failed to trigger DAG: {response.status_code} - {response.text}"
                logger.error(error_msg)

                return TriggerDAGResponse(
                    success=False,
                    message="Failed to trigger DAG",
                    error_message=error_msg,
                )

    except httpx.TimeoutException:
        logger.error(f"Timeout while triggering DAG {request.dag_id}")
        return TriggerDAGResponse(
            success=False,
            message="Request to Airflow timed out",
            error_message="Timeout connecting to Airflow",
        )
    except Exception as e:
        logger.error(f"Error triggering DAG {request.dag_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
