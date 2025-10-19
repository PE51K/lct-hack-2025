"""Routers package for ETL endpoints."""

from .create_dag import create_dag_router
from .create_etl import create_router
from .fetch_postgres_data import router as fetch_postgres_data_router
from .fetch_sample import fetch_sample_router
from .publish_etl import publish_router
from .trigger_dag import router as trigger_dag_router
from .update_etl import update_router
from .upload_file import upload_router

__all__ = [
    "create_dag_router",
    "create_router",
    "fetch_postgres_data_router",
    "fetch_sample_router",
    "publish_router",
    "trigger_dag_router",
    "update_router",
    "upload_router",
]
