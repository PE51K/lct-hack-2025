"""Models for data transformation configurations."""

from __future__ import annotations
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TransformationType(str, Enum):
    """Types of data transformations."""
    
    SQL = "sql"
    PYTHON = "python" 
    VALIDATION = "validation"
    AGGREGATION = "aggregation"
    ENRICHMENT = "enrichment"
    STANDARDIZATION = "standardization"
    CLEANING = "cleaning"


class ValidationRuleType(str, Enum):
    """Types of validation rules."""
    
    NOT_NULL = "not_null"
    RANGE = "range"
    REGEX = "regex"
    CUSTOM = "custom"
    DATA_TYPE = "data_type"
    UNIQUE = "unique"


class ErrorAction(str, Enum):
    """Actions to take when validation fails."""
    
    SKIP = "skip"
    FAIL = "fail"
    LOG = "log"
    DEFAULT = "default"


class TransformationRule(BaseModel):
    """Individual transformation rule."""
    
    rule_id: str
    rule_name: str
    description: str = ""
    transformation_type: TransformationType
    source_fields: list[str]
    target_field: str
    expression: str | None = None
    sql_query: str | None = None
    python_function: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    conditions: str | None = None
    priority: int = 1
    enabled: bool = True
    error_handling: ErrorAction = ErrorAction.SKIP


class ValidationRule(BaseModel):
    """Data validation rule."""
    
    field_name: str
    rule_type: ValidationRuleType
    parameters: dict[str, Any] = Field(default_factory=dict)
    error_action: ErrorAction = ErrorAction.SKIP
    error_message: str | None = None
    enabled: bool = True


class BusinessRule(BaseModel):
    """Business logic rule."""
    
    rule_name: str
    description: str = ""
    condition: str
    action: str
    priority: int = 1
    enabled: bool = True


class DataTypeMapping(BaseModel):
    """Mapping between source and target data types."""
    
    source_field: str
    source_type: str
    target_field: str
    target_type: str
    conversion_function: str | None = None
    default_value: Any | None = None


class TransformResourceConfig(BaseModel):
    """Resource configuration for transformation."""
    
    cpu_request: float = 2.0
    memory_request_mb: int = 1024
    execution_timeout_hours: float = 2.0
    parallel_workers: int = 2
    spill_to_disk: bool = False


class TransformConfig(BaseModel):
    """
    Enhanced configuration for data transformation steps.

    Attributes:
        identity_keys: List of attribute names or parsing paths that represent a unique entity.
        aggregate_keys: List of attribute names or parsing paths for aggregated unique entities.
        versioning_field: Field which represents version of entity.
        transformation_rules: List of transformation rules to apply
        validation_rules: List of data validation rules
        business_rules: List of business logic rules
        data_type_mappings: Mappings between source and target data types
        processing_mode: Processing mode (batch, streaming)
        resources: Resource configuration for transformation
    """

    identity_keys: list[str]
    aggregate_keys: list[str] = Field(default_factory=list)
    versioning_field: str | None = None
    transformation_rules: list[TransformationRule] = Field(default_factory=list)
    validation_rules: list[ValidationRule] = Field(default_factory=list)
    business_rules: list[BusinessRule] = Field(default_factory=list)
    data_type_mappings: list[DataTypeMapping] = Field(default_factory=list)
    processing_mode: str = "batch"
    window_size_minutes: int | None = None
    late_arrival_threshold_minutes: int = 60
    output_format: str = "table"
    partitioning_strategy: str | None = None
    sorting_keys: list[str] = Field(default_factory=list)
    resources: TransformResourceConfig = Field(default_factory=TransformResourceConfig)
