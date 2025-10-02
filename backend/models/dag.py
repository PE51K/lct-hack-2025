"""Directed Acyclic Graph models."""

from typing import Any

from pydantic import BaseModel, Field


class DAGTask(BaseModel):
    """Represents a single task in the DAG."""

    task_id: str = Field(..., description="Unique identifier for the task")
    task_type: str = Field(..., description="Type of task (extract, transform, load)")
    description: str = Field("", description="Human-readable description of the task")
    dependencies: list[str] = Field(default_factory=list, description="List of upstream task IDs")
    config: dict[str, Any] = Field(default_factory=dict, description="Task-specific configuration")


class DAG(BaseModel):
    """Represents a Directed Acyclic Graph structure."""

    dag_id: str = Field(..., description="Unique identifier for the DAG")
    description: str = Field("", description="Human-readable description of the DAG")
    tasks: list[DAGTask] = Field(default_factory=list, description="List of tasks in the DAG")
    schedule: str = Field("@daily", description="DAG schedule interval")
    owner: str = Field("", description="Owner of the DAG")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")
