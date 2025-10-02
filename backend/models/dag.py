"""Directed Acyclic Graph models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DAGTask(BaseModel):
    """Represents a single task in the DAG."""

    task_id: str = Field(..., description="Unique identifier for the task")
    task_type: str = Field(..., description="Type of task (extract, transform, load)")
    description: str = Field("", description="Human-readable description of the task")
    dependencies: list[str] = Field(default_factory=list, description="List of upstream task IDs")
    config: dict[str, Any] = Field(default_factory=dict, description="Task-specific configuration")
    operator_type: str = Field("PythonOperator", description="Airflow operator type")
    pool: str | None = Field(None, description="Airflow pool for resource management")
    pool_slots: int = Field(1, description="Number of pool slots required")
    execution_timeout_minutes: int = Field(60, description="Task execution timeout in minutes")
    retry_count: int = Field(3, description="Number of retries on failure")
    retry_delay_minutes: int = Field(5, description="Delay between retries in minutes")


class DAGDefaultArgs(BaseModel):
    """Default arguments for DAG tasks."""

    owner: str = Field(..., description="Owner of the DAG")
    depends_on_past: bool = Field(False, description="Whether task depends on past runs")
    start_date: datetime = Field(..., description="Start date for DAG scheduling")
    email_on_failure: bool = Field(True, description="Send email on task failure")
    email_on_retry: bool = Field(False, description="Send email on task retry")
    retries: int = Field(3, description="Default number of retries")
    retry_delay_minutes: int = Field(5, description="Default retry delay in minutes")
    execution_timeout_minutes: int = Field(60, description="Default execution timeout")


class DAG(BaseModel):
    """Represents a Directed Acyclic Graph structure for execution."""

    dag_id: str = Field(..., description="Unique identifier for the DAG")
    description: str = Field("", description="Human-readable description of the DAG")
    tasks: list[DAGTask] = Field(default_factory=list, description="List of tasks in the DAG")

    # Scheduling configuration
    schedule: str = Field("@daily", description="DAG schedule interval")
    start_date: datetime = Field(default_factory=lambda: datetime.now().replace(hour=2, minute=0, second=0, microsecond=0), description="DAG start date")
    end_date: datetime | None = Field(None, description="DAG end date")
    catchup: bool = Field(False, description="Whether to catch up on missed runs")
    max_active_runs: int = Field(1, description="Maximum number of active DAG runs")

    # Ownership and metadata
    owner: str = Field("", description="Owner of the DAG")
    team: str = Field("", description="Team responsible for the DAG")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")

    # Default arguments for tasks
    default_args: DAGDefaultArgs = Field(..., description="Default arguments for DAG tasks")

    # Execution configuration
    concurrency: int = Field(1, description="Maximum number of tasks that can run concurrently")
    max_active_tasks: int = Field(1, description="Maximum number of active tasks across all runs")

    # Resource requirements (estimated)
    estimated_runtime_minutes: int = Field(30, description="Estimated total runtime in minutes")
    total_cpu_cores: float = Field(1.0, description="Total CPU cores required")
    total_memory_mb: int = Field(1024, description="Total memory required in MB")

    # Airflow-specific settings
    dag_file_path: str | None = Field(None, description="Path to the generated DAG file")
    is_paused_upon_creation: bool = Field(True, description="Whether DAG should be paused when created")
    doc_md: str | None = Field(None, description="DAG documentation in Markdown format")
    
    # File generation support
    generated_files: dict[str, str] | None = Field(
        None,
        description="Paths to generated Airflow files (dag_file, functions_file, config_file, init_file)"
    )
