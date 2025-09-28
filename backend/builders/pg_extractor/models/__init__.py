"""
Top-level package for FCT ETL data models (mockups).

This package contains Pydantic models used across the ETL generation
pipeline (GUI → FastAPI → Callable/AI → Publisher/Airflow).

All models are **mockups** to unblock development and should be validated
and extended by domain owners (primarily Anton). Fields are intentionally
permissive (mostly optional) and to capture open questions.
"""

__all__ = [
    "ai",
    "common",
    "dag",
    "ddl",
    "extract",
    "generate_etl",
    "load",
    "publisher",
    "sources",
    "transform",
    "update_etl",
]
