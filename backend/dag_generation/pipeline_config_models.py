"""
Comprehensive ETL Pipeline Configuration Models

Этот модуль содержит полную архитектуру для создания ETL DAG-ов, включающую:
1. Расширенные конфигурации Extract, Transform, Load
2. AI рекомендации и оптимизации
3. Метрики производительности и качества данных
4. Полную схему для генерации Airflow DAG-ов

Процесс: Ссылка → Анализ → Извлечение → Трансформация → Загрузка → Мониторинг
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, List, Any, Union
from pydantic import BaseModel, Field

# ==============================================================================
# EXTRACT CONFIGURATION COMPONENTS
# ==============================================================================

class SourceType(str, Enum):
    """Types of data sources supported by the system."""
    
    FOLDER = "folder"
    POSTGRES = "postgres"  
    CLICKHOUSE = "clickhouse"
    KAFKA = "kafka"
    S3 = "s3"
    API = "api"
    FTP = "ftp"
    HDFS = "hdfs"


class ContentType(str, Enum):
    """Supported data formats."""
    
    XML = "xml"
    JSON = "json" 
    CSV = "csv"
    PARQUET = "parquet"
    AVRO = "avro"
    TABLE = "table"
    BINARY = "binary"


class DataQualityProfile(BaseModel):
    """Data quality metrics and thresholds."""
    
    completeness_threshold: float = Field(default=0.95, ge=0.0, le=1.0)
    accuracy_threshold: float = Field(default=0.98, ge=0.0, le=1.0)
    consistency_checks: List[str] = Field(default_factory=list)
    freshness_hours: int = Field(default=24, ge=1)
    volume_min_records: int = Field(default=1, ge=0)
    volume_max_records: Optional[int] = None
    schema_validation: bool = True
    duplicate_detection: bool = True
    schema_drift_detection: bool = True
    duplicate_threshold: float = Field(default=0.05, ge=0.0, le=1.0)


class SourceMetrics(BaseModel):
    """Metrics about the data source."""
    
    estimated_size_mb: float
    estimated_records: int
    file_count: Optional[int] = None
    avg_record_size_bytes: float
    complexity_score: float = Field(ge=0.0, le=10.0)
    nested_levels: int = Field(default=0, ge=0)
    unique_attributes: int
    nullable_attributes: int


class ExtractSchedule(BaseModel):
    """Scheduling configuration for data extraction."""
    
    frequency: str = Field(default="@daily")  # cron or preset
    start_date: datetime
    end_date: Optional[datetime] = None
    depends_on_past: bool = False
    max_active_runs: int = Field(default=1, ge=1)
    catchup: bool = False
    retry_count: int = Field(default=3, ge=0)
    retry_delay_minutes: int = Field(default=5, ge=1)
    execution_timeout_hours: int = Field(default=2, ge=1)


class ExtractResourceConfig(BaseModel):
    """Resource requirements for extraction."""
    
    cpu_cores: float = Field(default=1.0, ge=0.1)
    memory_mb: int = Field(default=512, ge=128)
    disk_space_mb: int = Field(default=1024, ge=100)
    network_bandwidth_mbps: Optional[float] = None
    parallel_workers: int = Field(default=1, ge=1)
    timeout_minutes: int = Field(default=60, ge=1)


class IncrementalConfig(BaseModel):
    """Configuration for incremental data loading."""
    
    enabled: bool = Field(default=False, description="Enable incremental loading")
    watermark_field: Optional[str] = Field(default=None, description="Watermark field")
    watermark_format: Optional[str] = Field(default=None, description="Watermark format")
    lookback_hours: int = Field(default=24, description="Lookback period in hours")
    state_storage: str = Field(default="airflow_variables", description="State storage")


class EnhancedExtractConfig(BaseModel):
    """Enhanced Extract configuration with complete metadata."""
    
    # Source identification
    source_id: str = Field(description="Unique identifier for the source")
    source_name: str = Field(description="Human readable source name")
    source_type: SourceType
    content_type: ContentType
    connection_string: str
    
    # Data characteristics  
    source_metrics: SourceMetrics
    data_quality: DataQualityProfile
    
    # Processing configuration
    batch_size: int = Field(default=1000, ge=1)
    incremental_config: IncrementalConfig
    
    # Schedule and resources
    schedule: ExtractSchedule
    resources: ExtractResourceConfig
    
    # Security and compliance
    encryption_required: bool = False
    pii_fields: List[str] = Field(default_factory=list)
    compliance_tags: List[str] = Field(default_factory=list)
    
    # Validation rules
    schema_validation_rules: Dict[str, Any] = Field(default_factory=dict)
    business_rules: List[str] = Field(default_factory=list)


# ==============================================================================
# TRANSFORM CONFIGURATION COMPONENTS  
# ==============================================================================

class TransformationType(str, Enum):
    """Types of data transformations."""
    
    CLEANSING = "cleansing"          # Data cleaning and normalization
    ENRICHMENT = "enrichment"        # Adding derived fields
    AGGREGATION = "aggregation"      # Grouping and summarizing  
    FILTERING = "filtering"          # Removing unwanted data
    JOINING = "joining"              # Combining datasets
    PIVOTING = "pivoting"            # Reshaping data
    VALIDATION = "validation"        # Data quality validation
    STANDARDIZATION = "standardization"  # Format standardization


class TransformationRule(BaseModel):
    """Individual transformation rule."""
    
    rule_id: str
    rule_name: str
    transformation_type: TransformationType
    source_fields: List[str]
    target_field: str
    expression: str  # SQL-like or Python expression
    conditions: Optional[str] = None  # When to apply the rule
    priority: int = Field(default=100, ge=1)  # Execution order
    error_handling: str = Field(default="skip")  # skip, fail, default_value


class DataTypeMapping(BaseModel):
    """Mapping between source and target data types."""
    
    source_field: str
    source_type: str
    target_field: str
    target_type: str
    conversion_function: Optional[str] = None
    default_value: Optional[Any] = None


class ValidationRule(BaseModel):
    """Data validation rule."""
    
    rule_name: str
    field_name: str
    validation_type: str  # not_null, range, format, custom
    parameters: Dict[str, Any] = Field(default_factory=dict)
    error_message: str
    severity: str = Field(default="error")  # warning, error, critical


class TransformResourceConfig(BaseModel):
    """Resource requirements for transformation."""
    
    cpu_cores: float = Field(default=2.0, ge=0.1)
    memory_mb: int = Field(default=2048, ge=256)
    temp_storage_mb: int = Field(default=5120, ge=512)
    max_parallelism: int = Field(default=4, ge=1)
    spill_to_disk: bool = True


class EnhancedTransformConfig(BaseModel):
    """Enhanced Transform configuration with complete rules."""
    
    # Transform identification
    transform_id: str
    transform_name: str
    description: str
    
    # Entity identification and versioning
    identity_keys: List[str]  # Primary key fields
    aggregate_keys: List[str]  # Fields for aggregation
    versioning_field: Optional[str] = None  # For SCD type 2
    
    # Transformation rules
    transformation_rules: List[TransformationRule]
    data_type_mappings: List[DataTypeMapping]
    validation_rules: List[ValidationRule]
    
    # Processing configuration
    processing_mode: str = Field(default="batch")  # batch, streaming, micro-batch
    window_size_minutes: Optional[int] = None  # For streaming
    late_arrival_threshold_minutes: int = Field(default=60)
    
    # Output configuration
    output_format: ContentType = ContentType.TABLE
    partitioning_strategy: Optional[str] = None
    sorting_keys: List[str] = Field(default_factory=list)
    
    # Resource and performance
    resources: TransformResourceConfig
    checkpoint_interval_minutes: int = Field(default=10, ge=1)
    
    # Quality and monitoring
    quality_checks: List[ValidationRule] = Field(default_factory=list)
    monitoring_metrics: List[str] = Field(default_factory=list)


# ==============================================================================
# LOAD CONFIGURATION COMPONENTS
# ==============================================================================

class TargetStorageType(str, Enum):
    """Target storage systems."""
    
    POSTGRES = "postgres"
    CLICKHOUSE = "clickhouse" 
    HDFS = "hdfs"
    S3 = "s3"
    KAFKA = "kafka"
    ELASTICSEARCH = "elasticsearch"
    REDIS = "redis"


class LoadStrategy(str, Enum):
    """Data loading strategies."""
    
    FULL_REFRESH = "full_refresh"     # Truncate and reload
    INCREMENTAL = "incremental"       # Append new data only
    MERGE = "merge"                   # Upsert based on key
    SCD_TYPE_1 = "scd_type_1"        # Slowly changing dimension type 1
    SCD_TYPE_2 = "scd_type_2"        # Slowly changing dimension type 2
    SNAPSHOT = "snapshot"             # Point-in-time snapshot


class IndexStrategy(BaseModel):
    """Database indexing strategy."""
    
    index_name: str
    index_type: str = Field(default="btree")  # btree, hash, gin, gist
    columns: List[str]
    is_unique: bool = False
    is_primary: bool = False
    is_clustered: bool = False
    fill_factor: Optional[int] = Field(default=None, ge=1, le=100)


class PartitionStrategy(BaseModel):
    """Data partitioning strategy."""
    
    partition_type: str = Field(default="range")  # range, list, hash
    partition_key: str
    partition_size: Optional[str] = None  # e.g., "monthly", "daily"
    retention_days: Optional[int] = None


class LoadResourceConfig(BaseModel):
    """Resource requirements for loading."""
    
    cpu_cores: float = Field(default=1.0, ge=0.1)
    memory_mb: int = Field(default=1024, ge=256)
    concurrent_connections: int = Field(default=5, ge=1, le=100)
    batch_size: int = Field(default=10000, ge=100)
    commit_frequency: int = Field(default=1000, ge=1)


class DataRetentionPolicy(BaseModel):
    """Data retention and archival policy."""
    
    retention_days: int = Field(ge=1)
    archive_after_days: Optional[int] = None
    compression_enabled: bool = True
    backup_frequency: str = "daily"  # daily, weekly, monthly


class CompressionConfig(BaseModel):
    """Configuration for data compression."""
    
    enabled: bool = Field(default=True, description="Enable compression")
    algorithm: str = Field(default="lz4", description="Compression algorithm")
    level: int = Field(default=1, description="Compression level")
    columns: Optional[List[str]] = Field(default=None, description="Columns to compress")


class DataQualityChecks(BaseModel):
    """Data quality checks after loading."""
    
    row_count_validation: bool = Field(default=True, description="Validate row count")
    null_checks: Dict[str, bool] = Field(default_factory=dict, description="NULL checks")
    unique_constraints: List[str] = Field(default_factory=list, description="Unique constraints")
    foreign_key_checks: List[str] = Field(default_factory=list, description="Foreign key checks")
    custom_sql_checks: List[str] = Field(default_factory=list, description="Custom SQL checks")


class EnhancedLoadConfig(BaseModel):
    """Enhanced Load configuration with complete target setup."""
    
    # Target identification
    load_id: str
    load_name: str
    description: str
    
    # Target configuration
    target_storage_type: TargetStorageType
    connection_string: str
    database_name: str
    schema_name: str
    table_name: str
    
    # Loading strategy
    load_strategy: LoadStrategy
    merge_keys: List[str] = Field(default_factory=list)  # For merge strategy
    update_fields: List[str] = Field(default_factory=list)
    
    # Schema and structure
    target_schema: List[DataTypeMapping]
    indexes: List[IndexStrategy] = Field(default_factory=list)
    partitioning: Optional[PartitionStrategy] = None
    compression: CompressionConfig
    
    # Performance optimization
    resources: LoadResourceConfig
    pre_load_sql: List[str] = Field(default_factory=list)  # Setup scripts
    post_load_sql: List[str] = Field(default_factory=list)  # Cleanup scripts
    
    # Data management
    retention_policy: Optional[DataRetentionPolicy] = None
    compression_type: Optional[str] = None
    
    # Monitoring and alerting
    quality_checks: DataQualityChecks
    success_metrics: List[str] = Field(default_factory=list)
    failure_thresholds: Dict[str, float] = Field(default_factory=dict)
    notification_channels: List[str] = Field(default_factory=list)


# ==============================================================================
# PIPELINE CONFIGURATION COMPONENTS
# ==============================================================================

class PipelineType(str, Enum):
    """Types of data pipelines."""
    
    BATCH_ETL = "batch_etl"
    STREAMING_ETL = "streaming_etl"
    REAL_TIME = "real_time"
    MICRO_BATCH = "micro_batch"
    LAMBDA_ARCHITECTURE = "lambda_architecture"


class DependencyType(str, Enum):
    """Types of task dependencies."""
    
    SUCCESS = "success"        # Wait for successful completion
    FAILURE = "failure"        # Trigger on failure
    COMPLETION = "completion"  # Trigger on any completion
    SENSOR = "sensor"          # Wait for external condition
    TIME_BASED = "time_based"  # Wait for specific time


class TaskDependency(BaseModel):
    """Task dependency definition."""
    
    upstream_task_id: str
    downstream_task_id: str
    dependency_type: DependencyType = DependencyType.SUCCESS
    wait_timeout_minutes: Optional[int] = None


class PipelineSchedule(BaseModel):
    """Pipeline scheduling configuration."""
    
    schedule_interval: str = "@daily"  # cron or preset
    start_date: datetime
    end_date: Optional[datetime] = None
    timezone: str = "UTC"
    depends_on_past: bool = False
    max_active_runs: int = 1
    catchup: bool = False


class NotificationConfig(BaseModel):
    """Pipeline notification configuration."""
    
    email_on_success: bool = False
    email_on_failure: bool = True
    email_on_retry: bool = False
    email_addresses: List[str] = Field(default_factory=list)
    slack_webhook: Optional[str] = None
    custom_callbacks: List[str] = Field(default_factory=list)


class PipelineMetadata(BaseModel):
    """Pipeline metadata and documentation."""
    
    pipeline_id: str
    pipeline_name: str
    description: str
    version: str = "1.0.0"
    owner: str
    team: str
    business_domain: str
    criticality: str = Field(default="medium")  # low, medium, high, critical
    documentation_url: Optional[str] = None
    source_code_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class EnhancedPipelineConfig(BaseModel):
    """Complete pipeline configuration."""
    
    # Pipeline metadata
    metadata: PipelineMetadata
    pipeline_type: PipelineType
    
    # ETL configurations
    extract_config: EnhancedExtractConfig
    transform_config: EnhancedTransformConfig
    load_config: EnhancedLoadConfig
    
    # Pipeline orchestration
    schedule: PipelineSchedule
    dependencies: List[TaskDependency] = Field(default_factory=list)
    
    # Monitoring and alerting
    notifications: NotificationConfig
    sla_minutes: Optional[int] = None  # Expected completion time
    
    # Environment and deployment
    environment: str = Field(default="development")  # dev, test, prod
    deployment_strategy: str = Field(default="blue_green")
    
    # Resource allocation
    total_cpu_cores: float = Field(default=4.0, ge=0.1)
    total_memory_mb: int = Field(default=8192, ge=512)
    estimated_runtime_minutes: int = Field(default=30, ge=1)
    
    # Data governance
    data_classification: str = Field(default="internal")  # public, internal, confidential, restricted
    gdpr_applicable: bool = False
    data_lineage_enabled: bool = True


# ==============================================================================
# AI RECOMMENDATION COMPONENTS
# ==============================================================================

class RecommendationType(str, Enum):
    """Types of AI recommendations."""
    
    STORAGE_OPTIMIZATION = "storage_optimization"
    PERFORMANCE_TUNING = "performance_tuning"
    RESOURCE_ALLOCATION = "resource_allocation"
    SCHEMA_OPTIMIZATION = "schema_optimization"
    INDEXING_STRATEGY = "indexing_strategy"
    PARTITIONING_STRATEGY = "partitioning_strategy"
    SCHEDULING_OPTIMIZATION = "scheduling_optimization"


class AIRecommendation(BaseModel):
    """AI-generated recommendation."""
    
    recommendation_id: str
    recommendation_type: RecommendationType
    title: str
    description: str
    rationale: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    impact_level: str = Field(default="medium")  # low, medium, high
    implementation_effort: str = Field(default="medium")  # low, medium, high
    estimated_improvement: Dict[str, float] = Field(default_factory=dict)
    implementation_steps: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    

class OptimizationMetrics(BaseModel):
    """Metrics for pipeline optimization."""
    
    throughput_records_per_minute: float
    latency_minutes: float
    resource_utilization_cpu: float = Field(ge=0.0, le=1.0)
    resource_utilization_memory: float = Field(ge=0.0, le=1.0)
    cost_per_execution_usd: float
    data_quality_score: float = Field(ge=0.0, le=1.0)
    reliability_score: float = Field(ge=0.0, le=1.0)


class CompletePipelineConfig(BaseModel):
    """Complete pipeline configuration."""
    
    # Pipeline metadata
    metadata: PipelineMetadata
    pipeline_type: PipelineType
    
    # ETL configurations
    extract_config: EnhancedExtractConfig
    transform_config: EnhancedTransformConfig
    load_config: EnhancedLoadConfig
    
    # Pipeline orchestration
    dependencies: List[TaskDependency] = Field(default_factory=list)
    
    # Monitoring and alerting
    notifications: NotificationConfig
    sla_minutes: Optional[int] = None  # Expected completion time
    
    # Environment and deployment
    environment: str = Field(default="development")  # dev, test, prod
    
    # Resource allocation
    total_cpu_cores: float = Field(default=4.0, ge=0.1)
    total_memory_mb: int = Field(default=8192, ge=512)
    estimated_runtime_minutes: int = Field(default=30, ge=1)
    
    # Data governance
    data_classification: str = Field(default="internal")  # public, internal, confidential, restricted
    gdpr_applicable: bool = False
    data_lineage_enabled: bool = True


class CompletePipelineWithAI(BaseModel):
    """Complete configuration for DAG generation with AI recommendations."""
    
    # Core pipeline configuration
    pipeline_config: CompletePipelineConfig
    
    # AI recommendations
    ai_recommendations: List[AIRecommendation] = Field(default_factory=list)
    
    # Performance baseline
    baseline_metrics: Optional[OptimizationMetrics] = None
    target_metrics: Optional[OptimizationMetrics] = None
    
    # Generation metadata
    generated_at: datetime = Field(default_factory=datetime.now)
    generator_version: str = "2.0.0"
    config_hash: Optional[str] = None  # For change detection