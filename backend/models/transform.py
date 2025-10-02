"""Models for data transformation configurations."""

from enum import Enum
from typing import Annotated, Any

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

    rule_id: str = Field(..., description="Unique identifier for the rule.")
    rule_name: str = Field(..., description="Name of the rule.")
    description: str = Field("", description="Description of the rule.")
    transformation_type: Annotated[str, TransformationType] = Field(
        ..., description="Type of transformation."
    )
    source_fields: list[str] = Field(..., description="Source fields for the transformation.")
    target_field: str = Field(..., description="Target field for the transformation.")
    expression: str | None = Field(None, description="Expression for the transformation.")
    sql_query: str | None = Field(None, description="SQL query for the transformation.")
    python_function: str | None = Field(None, description="Python function for the transformation.")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Parameters for the transformation."
    )
    conditions: str | None = Field(None, description="Conditions for the transformation.")
    priority: int = Field(1, description="Priority of the rule.")
    enabled: bool = Field(True, description="Whether the rule is enabled.")
    error_handling: Annotated[str, ErrorAction] = Field(
        ErrorAction.SKIP, description="Error handling strategy."
    )


class ValidationRule(BaseModel):
    """Data validation rule."""

    field_name: str = Field(..., description="Name of the field to validate.")
    rule_type: Annotated[str, ValidationRuleType] = Field(
        ..., description="Type of validation rule."
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Parameters for the validation rule."
    )
    error_action: Annotated[str, ErrorAction] = Field(
        ErrorAction.SKIP, description="Action to take on validation error."
    )
    error_message: str | None = Field(None, description="Custom error message.")
    enabled: bool = Field(True, description="Whether the rule is enabled.")


class BusinessRule(BaseModel):
    """Business logic rule."""

    rule_name: str = Field(..., description="Name of the business rule.")
    description: str = Field("", description="Description of the business rule.")
    condition: str = Field(..., description="Condition for the business rule.")
    action: str = Field(..., description="Action for the business rule.")
    priority: int = Field(1, description="Priority of the business rule.")
    enabled: bool = Field(True, description="Whether the business rule is enabled.")


class DataTypeMapping(BaseModel):
    """Mapping between source and target data types."""

    source_field: str = Field(..., description="Source field name.")
    source_type: str = Field(..., description="Source data type.")
    target_field: str = Field(..., description="Target field name.")
    target_type: str = Field(..., description="Target data type.")
    conversion_function: str | None = Field(None, description="Conversion function.")
    default_value: Any | None = Field(None, description="Default value.")


class TransformResourceConfig(BaseModel):
    """Resource configuration for transformation."""

    cpu_request: float = Field(2.0, description="CPU request.")
    memory_request_mb: int = Field(1024, description="Memory request in MB.")
    execution_timeout_hours: float = Field(2.0, description="Execution timeout in hours.")
    parallel_workers: int = Field(2, description="Number of parallel workers.")
    spill_to_disk: bool = Field(False, description="Whether to spill to disk.")


class TransformConfig(BaseModel):
    """Enhanced configuration for data transformation steps."""

    identity_keys: list[str] = Field(
        ..., description="List of attribute names or parsing paths that represent a unique entity."
    )
    aggregate_keys: list[str] = Field(
        default_factory=list,
        description="List of attribute names or parsing paths for aggregated unique entities.",
    )
    versioning_field: str | None = Field(
        None, description="Field which represents version of entity."
    )
    transformation_rules: list[TransformationRule] = Field(
        default_factory=list, description="List of transformation rules to apply."
    )
    validation_rules: list[ValidationRule] = Field(
        default_factory=list, description="List of data validation rules."
    )
    business_rules: list[BusinessRule] = Field(
        default_factory=list, description="List of business logic rules."
    )
    data_type_mappings: list[DataTypeMapping] = Field(
        default_factory=list, description="Mappings between source and target data types."
    )
    processing_mode: str = Field("batch", description="Processing mode.")
    window_size_minutes: int | None = Field(None, description="Window size in minutes.")
    late_arrival_threshold_minutes: int = Field(
        60, description="Late arrival threshold in minutes."
    )
    output_format: str = Field("table", description="Output format.")
    partitioning_strategy: str | None = Field(None, description="Partitioning strategy.")
    sorting_keys: list[str] = Field(default_factory=list, description="Sorting keys.")
    resources: TransformResourceConfig = Field(
        default_factory=TransformResourceConfig,
        description="Resource configuration for transformation.",
    )
