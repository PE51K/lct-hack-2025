# DAGBuilder Deep Dive

**Complete Technical Explanation**

---

## Overview

[`DAGBuilder`](../builders/dag/builder.py) is the core component that creates Airflow DAG configuration models from your ETL configs. It acts as the **orchestration architect** that designs the workflow structure before any code is generated.

```mermaid
graph LR
    A[ExtractConfig] --> D[DAGBuilder]
    B[TransformConfig] --> D
    C[LoadConfig] --> D
    E[DDL] --> D
    D --> F[DAG Model]
    F --> G[AirflowFileGenerator]
    G --> H[Python Files]
```

---

## What DAGBuilder Uses

### Input Components

DAGBuilder receives **4 configuration objects**:

#### 1. ExtractConfig
**Location**: [`backend/models/extract.py`](../models/extract.py)

**What it contains**:
```python
ExtractConfig:
  ├── source_metadata: Source
  │   ├── source_type: "folder" | "PostgreSQL" | "ClickHouse" | "kafka" | "s3"
  │   ├── connection_string: str  # Connection details
  │   ├── table_name: str | None  # For PostgreSQL
  │   ├── bucket_name: str | None # For S3
  │   ├── access_key: str | None  # For S3
  │   └── secret_key: str | None  # For S3
  ├── content_metadata: list[Content]
  │   └── [file/topic/table details with metamodel]
  ├── schedule: ExtractSchedule
  │   ├── interval: "@daily" | "@hourly" | cron
  │   ├── start_date: str
  │   ├── catchup: bool
  │   └── max_active_runs: int
  ├── resources: ExtractResourceConfig
  │   ├── cpu_request: float
  │   ├── memory_request_mb: int
  │   ├── parallel_workers: int
  │   └── timeout_minutes: int
  ├── data_quality: DataQualityProfile
  │   ├── completeness_threshold: float
  │   ├── accuracy_threshold: float
  │   └── schema_drift_detection: bool
  └── batch_size: int
```

**Purpose**: Defines **where** and **how** to extract data.

#### 2. TransformConfig
**Location**: [`backend/models/transform.py`](../models/transform.py)

**What it contains**:
```python
TransformConfig:
  ├── identity_keys: list[str]  # Unique entity identifiers
  ├── transformation_rules: list[TransformationRule]
  │   ├── rule_id, rule_name
  │   ├── transformation_type: "sql" | "python" | "validation" | etc.
  │   ├── source_fields, target_field
  │   ├── expression: str | None
  │   ├── sql_query: str | None
  │   └── python_function: str | None
  ├── validation_rules: list[ValidationRule]
  │   ├── field_name
  │   ├── rule_type: "not_null" | "range" | "regex" | etc.
  │   └── error_action: "skip" | "fail" | "log"
  ├── business_rules: list[BusinessRule]
  ├── data_type_mappings: list[DataTypeMapping]
  ├── processing_mode: "batch" | "streaming"
  └── resources: TransformResourceConfig
      ├── cpu_request: float
      ├── memory_request_mb: int
      └── parallel_workers: int
```

**Purpose**: Defines **what transformations** to apply to data.

#### 3. LoadConfig
**Location**: [`backend/models/load.py`](../models/load.py)

**What it contains**:
```python
LoadConfig:
  ├── target_storage_type: TargetStorageTypeRecommendation
  │   ├── storage_type: "postgres" | "clickhouse" | "hdfs"
  │   └── explanation: str
  ├── target_storage_connection_string: str  # Target DB connection
  │   # NOTE: Connection string alone is NOT enough!
  │   # Missing explicit fields (see ISSUE below)
  ├── flat_meta_model: FlatMetaModel  # For postgres/clickhouse
  │   ├── fields: list[ColumnField]
  │   │   ├── name, data_type
  │   │   └── nullable, indexing_order
  │   ├── indexes: list[Index]
  │   └── partitioning_key: str
  ├── nesting_metamodel: NestingMetaModel  # For HDFS
  ├── load_strategy: "append" | "upsert" | "full_refresh" | "incremental"
  ├── batch_config: BatchConfig
  │   ├── batch_size: int
  │   ├── parallel_loads: int
  │   └── error_threshold: float
  ├── partitioning: PartitioningConfig
  ├── indexing: IndexingConfig
  ├── compression: CompressionConfig
  └── resources: LoadResourceConfig
      ├── connection_pool_size: int
      └── timeout_minutes: int
```

**Purpose**: Defines **where** and **how** to load transformed data.

#### 4. DDL (Data Definition Language)
**Location**: [`backend/models/ddl.py`](../models/ddl.py)

**What it contains**:
```python
DDL:
  ├── statements: str  # Full CREATE TABLE SQL
  ├── target_database: str
  ├── target_schema: str
  ├── target_table: str
  └── columns: list[ColumnDefinition]
      ├── name, data_type
      ├── is_primary_key, is_nullable
      └── constraints
```

**Purpose**: Defines **table schemas** for the target database.

---

## What DAGBuilder Produces

### Output: DAG Model

**Location**: [`backend/models/dag.py`](../models/dag.py)

```python
DAG:
  ├── dag_id: str  # "etl_folder_postgres_20251002_120000"
  ├── description: str
  ├── schedule: str  # "@daily", "@hourly", cron expression
  ├── start_date: datetime
  ├── catchup: bool
  ├── max_active_runs: int
  ├── owner: str  # "data_team"
  ├── team: str   # "data_engineering"
  ├── tags: list[str]  # ["etl", "auto_generated", "folder", "postgres"]
  ├── default_args: DAGDefaultArgs
  │   ├── owner, depends_on_past
  │   ├── start_date
  │   ├── email_on_failure, email_on_retry
  │   ├── retries: int (3)
  │   ├── retry_delay_minutes: int (5)
  │   └── execution_timeout_minutes: int (60)
  ├── tasks: list[DAGTask]
  │   └── [extract_data, transform_data, load_data]
  ├── concurrency: int
  ├── max_active_tasks: int
  ├── estimated_runtime_minutes: int
  ├── total_cpu_cores: float
  ├── total_memory_mb: int
  ├── is_paused_upon_creation: bool
  ├── doc_md: str  # Markdown documentation
  ├── generated_files: dict[str, str] | None  # Added by FileGenerator
  └── dag_file_path: str | None  # Added by FileGenerator
```

### Generated Tasks Structure

DAGBuilder creates **3 main tasks**:

```python
tasks = [
    DAGTask(
        task_id="extract_data",
        task_type="extract",
        description="Extract data from {source_type} source",
        dependencies=[],  # No dependencies, runs first
        config={
            "source_type": "folder",
            "connection_string": "file:///data/source",
            "batch_size": 1000
        },
        operator_type="PythonOperator",
        pool_slots=1,
        execution_timeout_minutes=30,
        retry_count=3,
        retry_delay_minutes=5
    ),
    
    DAGTask(
        task_id="transform_data",
        task_type="transform",
        description="Apply data transformations",
        dependencies=["extract_data"],  # Runs after extract
        config={
            "rules_count": 5,
            "identity_keys": ["id", "timestamp"],
            "processing_mode": "batch"
        },
        operator_type="PythonOperator",
        pool_slots=2,
        execution_timeout_minutes=45,
        retry_count=2
    ),
    
    DAGTask(
        task_id="load_data",
        task_type="load",
        description="Load to postgres",
        dependencies=["transform_data"],  # Runs after transform
        config={
            "target_type": "postgres",
            "table_name": "analytics.processed_data",
            "load_strategy": "append",
            "batch_size": 1000
        },
        operator_type="PythonOperator",
        pool_slots=1,
        execution_timeout_minutes=30,
        retry_count=3
    )
]
```

**Task Flow**: `extract_data` → `transform_data` → `load_data`

---

## Supported Source/Target Types

### Source Database Types

From [`ExtractConfig.source_metadata.source_type`](../models/extract.py:100-108):

| Source Type | Description | Connection String Example |
|-------------|-------------|---------------------------|
| **folder** | Local filesystem/mounted directory | `file:///data/source` |
| **PostgreSQL** | PostgreSQL database | `postgresql://user:pass@host:5432/db` |
| **ClickHouse** | ClickHouse database | `clickhouse://user:pass@host:8123/db` |
| **kafka** | Apache Kafka topics | `kafka://broker:9092` |
| **s3** | AWS S3 buckets | `s3://bucket-name` |

**Implementation**: Each source type has a builder in [`backend/builders/extract/`](../builders/extract/):
- [`folder.py`](../builders/extract/folder.py) - File-based sources (CSV, JSON, XML)
- [`postgres.py`](../builders/extract/postgres.py) - PostgreSQL databases
- [`clickhouse.py`](../builders/extract/clickhouse.py) - ClickHouse databases
- [`kafka.py`](../builders/extract/kafka.py) - Kafka streams
- [`s3.py`](../builders/extract/s3.py) - S3 object storage

### Target Database Types

From [`LoadConfig.target_storage_type`](../models/load.py:9-14):

| Target Type | Description | Use Case |
|-------------|-------------|----------|
| **postgres** | PostgreSQL | OLTP, relational data, complex queries |
| **clickhouse** | ClickHouse | OLAP, analytics, time-series, high-volume |
| **hdfs** | Hadoop HDFS | Big data, unstructured data, data lake |

**Configuration**: Target is determined by AI recommendation in [`LoadConfig.target_storage_type.storage_type`](../models/load.py:17-27).

### Content/File Types

From [`ExtractConfig.content_metadata.content_type`](../models/extract.py:111-118):

| Content Type | Description | Supported Sources |
|--------------|-------------|-------------------|
| **csv** | CSV files | folder, s3 |
| **json** | JSON files/messages | folder, s3, kafka |
| **xml** | XML files | folder, s3 |
| **table** | Database tables | PostgreSQL, ClickHouse |

---

## Supported Transformations

### Transformation Types

From [`TransformConfig.transformation_rules[].transformation_type`](../models/transform.py:9-18):

| Type | Description | Use Case |
|------|-------------|----------|
| **sql** | SQL expressions | Column calculations, joins, aggregations |
| **python** | Python functions | Complex logic, custom processing |
| **validation** | Data validation | Check data quality, constraints |
| **aggregation** | Aggregate operations | SUM, AVG, COUNT, GROUP BY |
| **enrichment** | Data enrichment | Add derived columns, lookups |
| **standardization** | Format standardization | Date formats, case normalization |
| **cleaning** | Data cleaning | Null handling, trimming, deduplication |

### Example Transformation Rules

```python
transformation_rules = [
    TransformationRule(
        rule_id="clean_email",
        rule_name="Normalize Email",
        transformation_type="standardization",
        source_fields=["email"],
        target_field="email_normalized",
        expression="LOWER(TRIM(email))",
        priority=1
    ),
    
    TransformationRule(
        rule_id="calc_total",
        rule_name="Calculate Total",
        transformation_type="sql",
        source_fields=["quantity", "price"],
        target_field="total_amount",
        sql_query="quantity * price",
        priority=2
    ),
    
    TransformationRule(
        rule_id="validate_age",
        rule_name="Validate Age Range",
        transformation_type="validation",
        source_fields=["age"],
        target_field="age",
        expression="age >= 0 AND age <= 120",
        error_handling="skip"  # Skip invalid records
    )
]
```

### Validation Rules

From [`TransformConfig.validation_rules[].rule_type`](../models/transform.py:21-29):

| Validation Type | Description | Example |
|-----------------|-------------|---------|
| **not_null** | Field must not be null | Required fields |
| **range** | Value within range | Age between 0-120 |
| **regex** | Match regex pattern | Email format, phone |
| **data_type** | Correct data type | Integer, Date |
| **unique** | No duplicates | Primary keys |
| **custom** | Custom Python logic | Business rules |

---

## How Credentials Are Acquired

### Source Credentials

Credentials come from [`ExtractConfig.source_metadata`](../models/extract.py:121-141):

```python
# For PostgreSQL/ClickHouse
source_metadata = Source(
    source_type="PostgreSQL",
    connection_string="postgresql://user:password@host:5432/database",
    table_name="source_table"
)

# For S3
source_metadata = Source(
    source_type="s3",
    connection_string="s3://bucket-name/path/",
    bucket_name="my-bucket",
    access_key="AKIAIOSFODNN7EXAMPLE",
    secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
)

# For Kafka
source_metadata = Source(
    source_type="kafka",
    connection_string="kafka://broker1:9092,broker2:9092",
    # Additional kafka config in content_metadata
)

# For Folder (no credentials needed)
source_metadata = Source(
    source_type="folder",
    connection_string="file:///data/source"
)
```

**Security Note**: Connection strings contain credentials. In production:
- Use environment variables: `postgresql://${DB_USER}:${DB_PASSWORD}@...`
- Use Airflow Connections: Reference by connection ID
- Use secrets manager: AWS Secrets Manager, HashiCorp Vault

### Target Credentials

Credentials come from [`LoadConfig.target_storage_connection_string`](../models/load.py:156-158):

```python
target_storage_connection_string = "postgresql://user:password@host:5432/target_db"
```

**In Generated DAG Files**:

The [`AirflowFileGenerator`](../builders/dag/file_generator.py) embeds these in the config file:

```python
# Generated: etl_user_thread_config.py
SOURCE_CONNECTION = "postgresql://user:pass@source:5432/db"
TARGET_CONNECTION = "postgresql://user:pass@target:5432/db"
```

**Best Practice**: Replace with Airflow connection references in production:

```python
# Use Airflow Connections instead
from airflow.hooks.postgres_hook import PostgresHook

source_hook = PostgresHook(postgres_conn_id='source_db')
target_hook = PostgresHook(postgres_conn_id='target_db')
```

---

## How DAG Folder Is Set

### In DAGBuilder

[`DAGBuilder`](../builders/dag/builder.py) **does not** set the folder - it only creates the **model**.

The folder path is determined by [`AirflowFileGenerator`](../builders/dag/file_generator.py).

### In AirflowFileGenerator

**Location**: [`backend/builders/dag/file_generator.py:22-38`](../builders/dag/file_generator.py)

```python
class AirflowFileGenerator:
    def __init__(self, base_output_dir: Path | str = "dags"):
        # Resolve path relative to file_generator.py location
        if not Path(base_output_dir).is_absolute():
            # Get backend directory (3 levels up from this file)
            backend_dir = Path(__file__).parent.parent.parent
            self.base_output_dir = backend_dir / base_output_dir
        else:
            self.base_output_dir = Path(base_output_dir)
        
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
```

**Default Configuration**:
- `base_output_dir = "dags"` (relative)
- Resolves to: `backend/dags/`
- Creates subdirectories: `backend/dags/{user_id}/{thread_id}/`

**Path Resolution Logic**:

```python
# In generate_dag_files()
output_dir = self.base_output_dir / user_id / thread_id
output_dir.mkdir(parents=True, exist_ok=True)
```

**Example**:
```
Input:
  user_id = "user_123"
  thread_id = "thread_456"

Output Directory:
  backend/dags/user_123/thread_456/

Generated Files:
  backend/dags/user_123/thread_456/
    ├── etl_user_123_thread_456.py
    ├── etl_user_123_thread_456_functions.py
    ├── etl_user_123_thread_456_config.py
    └── __init__.py
```

### Customizing DAG Folder

**Option 1**: Change default in initialization
```python
# In create_etl.py
file_generator = AirflowFileGenerator(base_output_dir="/custom/path/dags")
```

**Option 2**: Use absolute path
```python
file_generator = AirflowFileGenerator(base_output_dir="/opt/airflow/dags")
```

**Option 3**: Environment variable (not currently implemented, but could be)
```python
import os
base_dir = os.getenv("AIRFLOW_DAGS_DIR", "dags")
file_generator = AirflowFileGenerator(base_output_dir=base_dir)
```

### Docker Volume Mount

The folder must be mounted to Airflow container:

```yaml
# docker-compose.airflow.yaml
volumes:
  - ${AIRFLOW_DAGS_VOLUME:-./dags}:/opt/airflow/dags
```

**Mapping**:
- Host: `backend/dags/` (where files are written)
- Container: `/opt/airflow/dags/` (where Airflow reads)

---

## Complete Flow Example

### Step-by-Step Generation

```python
# 1. User makes request
POST /create_etl
{
  "ids": {"user_id": "user_123", "thread_id": "thread_456"},
  "user_prompt": "Extract from PostgreSQL, transform, load to ClickHouse"
}

# 2. ExtractConfigBuilder generates
extract_config = ExtractConfig(
    source_metadata=Source(
        source_type="PostgreSQL",
        connection_string="postgresql://user:pass@source:5432/db",
        table_name="orders"
    ),
    batch_size=1000,
    resources=ExtractResourceConfig(parallel_workers=2)
)

# 3. LoadConfigBuilder generates
load_config = LoadConfig(
    target_storage_type=TargetStorageTypeRecommendation(
        storage_type="clickhouse",
        explanation="OLAP workload"
    ),
    target_storage_connection_string="clickhouse://user:pass@target:8123/db",
    flat_meta_model=FlatMetaModel(
        fields=[
            ColumnField(name="order_id", data_type="Int64"),
            ColumnField(name="customer_id", data_type="Int64"),
            ColumnField(name="total", data_type="Decimal(10,2)")
        ]
    ),
    load_strategy="append"
)

# 4. TransformConfigBuilder generates
transform_config = TransformConfig(
    identity_keys=["order_id"],
    transformation_rules=[
        TransformationRule(
            rule_name="Calculate Tax",
            transformation_type="sql",
            source_fields=["total"],
            target_field="tax_amount",
            expression="total * 0.08"
        )
    ]
)

# 5. DDLBuilder generates
ddl = DDL(
    statements="""
        CREATE TABLE analytics.orders (
            order_id Int64,
            customer_id Int64,
            total Decimal(10,2),
            tax_amount Decimal(10,2)
        ) ENGINE = MergeTree()
        ORDER BY order_id
    """,
    target_database="analytics",
    target_schema="public",
    target_table="orders"
)

# 6. DAGBuilder creates DAG model
dag_builder = DAGBuilder()
dag = await dag_builder(extract_config, transform_config, load_config, ddl)

# Result:
dag = DAG(
    dag_id="etl_PostgreSQL_clickhouse_20251002_120000",
    description="ETL pipeline extracting from PostgreSQL and loading to clickhouse",
    schedule="@daily",
    tasks=[
        DAGTask(task_id="extract_data", ...),
        DAGTask(task_id="transform_data", ...),
        DAGTask(task_id="load_data", ...)
    ],
    estimated_runtime_minutes=65,
    total_cpu_cores=2.5,
    total_memory_mb=2560
)

# 7. AirflowFileGenerator creates Python files
file_generator = AirflowFileGenerator()
generated_files = await file_generator.generate_dag_files(
    dag=dag,
    extract_config=extract_config,
    transform_config=transform_config,
    load_config=load_config,
    ddl=ddl,
    user_id="user_123",
    thread_id="thread_456"
)

# Result:
generated_files = {
    "dag_file": "backend/dags/user_123/thread_456/etl_user_123_thread_456.py",
    "functions_file": "backend/dags/user_123/thread_456/etl_user_123_thread_456_functions.py",
    "config_file": "backend/dags/user_123/thread_456/etl_user_123_thread_456_config.py",
    "init_file": "backend/dags/user_123/thread_456/__init__.py"
}

# 8. Airflow discovers and executes
# (after 30-60 seconds)
```

---

## Key Methods in DAGBuilder

### Main Method: `__call__()`

```python
async def __call__(
    self,
    extract_config: ExtractConfig,
    transform_config: TransformConfig,
    load_config: LoadConfig,
    ddl: DDL,
) -> DAG
```

**Process**:
1. Generate DAG ID: `_generate_dag_id()`
2. Generate description: `_generate_description()`
3. Generate tasks: `_generate_tasks()`
4. Generate default args: `_generate_default_args()`
5. Estimate resources: `_estimate_runtime()`, `_estimate_cpu_requirements()`, `_estimate_memory_requirements()`
6. Generate documentation: `_generate_documentation()`
7. Return DAG model

### Helper Methods

#### `_generate_dag_id()`
```python
def _generate_dag_id(self, extract_config: ExtractConfig, load_config: LoadConfig) -> str:
    source_type = extract_config.source_metadata.source_type
    target_type = load_config.target_storage_type.storage_type
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"etl_{source_type}_{target_type}_{timestamp}"
```

#### `_generate_tasks()`
Creates 3 tasks with proper dependencies:
- Extract → Transform → Load

#### `_estimate_runtime()`
Calculates expected runtime based on:
- Data size
- Number of transformation rules
- Load strategy
- Historical patterns

---

## Summary

### DAGBuilder Role

**Input**: 4 configuration objects (Extract, Transform, Load, DDL)  
**Output**: DAG model (JSON/Pydantic structure)  
**Purpose**: Orchestration design, not code generation

### Supported Types

**Sources**: folder, PostgreSQL, ClickHouse, kafka, s3  
**Targets**: postgres, clickhouse, hdfs  
**Content**: csv, json, xml, table  
**Transforms**: sql, python, validation, aggregation, enrichment, standardization, cleaning

### Credentials

**Source**: `ExtractConfig.source_metadata.connection_string` + optional keys  
**Target**: `LoadConfig.target_storage_connection_string`  
**Security**: Should use Airflow Connections or secrets manager in production

### DAG Folder

**Default**: `backend/dags/{user_id}/{thread_id}/`  
**Set by**: `AirflowFileGenerator(base_output_dir="dags")`  
**Mounted to**: `/opt/airflow/dags/` in Docker container  
**Discoverable**: Airflow scans every 30 seconds

---

**For implementation details, see**: [`backend/builders/dag/builder.py`](../builders/dag/builder.py)