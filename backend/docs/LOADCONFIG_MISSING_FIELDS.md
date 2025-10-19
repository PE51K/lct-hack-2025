# LoadConfig Missing Fields - Critical Issue

**Status**: ⚠️ **Current LoadConfig Model is Incomplete**

---

## Problem

The current [`LoadConfig`](../models/load.py) model is **missing essential fields** for properly identifying the target table location.

### What's Missing

```python
# These fields DO NOT EXIST in backend/models/load.py
database_name: str  # Target database name
schema_name: str    # Target schema (e.g., "public", "analytics")
table_name: str     # Target table name
```

### Current Workaround (Hacky Solution)

In [`DAGBuilder._generate_tasks()`](../builders/dag/builder.py:152-157):

```python
# Line 152-154: Derives table name from first field name (!)
table_name = (
    load_config.flat_meta_model.fields[0].name
    if load_config.flat_meta_model.fields
    else "target_table"
)
```

This is **not correct** because:
1. Field name ≠ Table name
2. No way to specify database or schema
3. Breaks for complex table structures

---

## What Each Target Type Needs

### PostgreSQL

**Required**:
```python
database_name: str    # e.g., "analytics_db"
schema_name: str      # e.g., "public", "raw", "staging"
table_name: str       # e.g., "customer_orders"
```

**Full Table Reference**: `database_name.schema_name.table_name`
- Example: `analytics_db.public.customer_orders`
- Connection: `postgresql://user:pass@host:5432/analytics_db`
- DDL: `CREATE TABLE public.customer_orders (...)`

### ClickHouse

**Required**:
```python
database_name: str    # e.g., "analytics"
schema_name: str      # Usually "default" or empty (ClickHouse uses database.table)
table_name: str       # e.g., "events"
```

**Full Table Reference**: `database_name.table_name` (schema often not used)
- Example: `analytics.events`
- Connection: `clickhouse://user:pass@host:8123/analytics`
- DDL: `CREATE TABLE analytics.events (...) ENGINE = MergeTree()`

**Note**: ClickHouse doesn't use schemas the same way PostgreSQL does. Usually just `database.table`.

### HDFS (Hadoop Distributed File System)

**Required**:
```python
hdfs_path: str        # Full HDFS path
database_name: str    # Hive database name (if using Hive metastore)
table_name: str       # Hive table name (if using Hive metastore)
```

**Different Structure**:
- HDFS stores files, not tables
- If using **Hive** on top of HDFS:
  - `database_name`: Hive database (e.g., "default", "analytics")
  - `table_name`: Hive table name (e.g., "events")
  - Path: `/user/hive/warehouse/analytics.db/events/`

**Options for HDFS**:

1. **Raw HDFS Files** (no Hive):
   ```python
   hdfs_path: str = "/data/analytics/events/"
   file_format: str = "parquet"  # parquet, orc, avro, json
   partition_pattern: str = "year={year}/month={month}/day={day}/"
   ```

2. **Hive Tables** (HDFS + metastore):
   ```python
   database_name: str = "analytics"
   table_name: str = "events"
   # Hive manages the HDFS path automatically
   ```

---

## Comparison: Current vs Should Be

### Current LoadConfig (backend/models/load.py)

```python
class LoadConfig(BaseModel):
    target_storage_type: TargetStorageTypeRecommendation
    target_storage_connection_string: str  # ⚠️ NOT ENOUGH!
    flat_meta_model: FlatMetaModel
    nesting_metamodel: NestingMetaModel
    load_strategy: str
    batch_config: BatchConfig
    # ... other configs
```

**Problems**:
- ❌ No `database_name`
- ❌ No `schema_name`
- ❌ No `table_name`
- ❌ No HDFS-specific fields

### Backend/stuff LoadConfig (backend/stuff/dag_generation/pipeline_config_models.py)

```python
class LoadConfig(BaseModel):
    target_storage_type: TargetStorageType
    connection_string: str
    database_name: str     # ✅ HAS THIS
    schema_name: str       # ✅ HAS THIS
    table_name: str        # ✅ HAS THIS
    # ... other configs
```

**This is better!** Has explicit fields for table location.

---

## Recommended LoadConfig Structure

### For PostgreSQL & ClickHouse

```python
class LoadConfig(BaseModel):
    target_storage_type: TargetStorageTypeRecommendation
    target_storage_connection_string: str
    
    # ADD THESE FIELDS:
    database_name: str = Field(..., description="Target database name")
    schema_name: str = Field(
        "public",  # Default for PostgreSQL
        description="Target schema name (use 'default' for ClickHouse)"
    )
    table_name: str = Field(..., description="Target table name")
    
    flat_meta_model: FlatMetaModel
    nesting_metamodel: NestingMetaModel
    load_strategy: str
    # ... rest of fields
```

### For HDFS (Additional Fields)

```python
class HDFSConfig(BaseModel):
    """HDFS-specific configuration."""
    
    hdfs_path: str = Field(..., description="Base HDFS path")
    file_format: str = Field("parquet", description="File format: parquet, orc, avro, json")
    
    # If using Hive metastore
    use_hive: bool = Field(False, description="Use Hive metastore")
    hive_database: str | None = Field(None, description="Hive database name")
    hive_table: str | None = Field(None, description="Hive table name")
    
    # Partitioning
    partition_columns: list[str] = Field(default_factory=list)
    partition_pattern: str | None = Field(None, description="Partition path pattern")
    
    # Compression
    compression: str = Field("snappy", description="Compression: snappy, gzip, lz4")

class LoadConfig(BaseModel):
    # ... existing fields ...
    
    # Add conditional HDFS config
    hdfs_config: HDFSConfig | None = Field(
        None,
        description="HDFS-specific configuration (required when target_storage_type is HDFS)"
    )
```

---

## Usage Examples

### PostgreSQL Example

```python
load_config = LoadConfig(
    target_storage_type=TargetStorageTypeRecommendation(
        storage_type="postgres",
        explanation="OLTP workload with complex queries"
    ),
    target_storage_connection_string="postgresql://user:pass@host:5432/analytics_db",
    database_name="analytics_db",
    schema_name="public",
    table_name="customer_orders",
    flat_meta_model=FlatMetaModel(
        fields=[
            ColumnField(name="order_id", data_type="BIGINT"),
            ColumnField(name="customer_id", data_type="BIGINT"),
            ColumnField(name="total", data_type="DECIMAL(10,2)")
        ],
        partitioning_key="created_date"
    ),
    load_strategy="append"
)

# Full table reference: analytics_db.public.customer_orders
```

### ClickHouse Example

```python
load_config = LoadConfig(
    target_storage_type=TargetStorageTypeRecommendation(
        storage_type="clickhouse",
        explanation="High-volume analytics queries"
    ),
    target_storage_connection_string="clickhouse://user:pass@host:8123/analytics",
    database_name="analytics",
    schema_name="default",  # ClickHouse usually uses "default"
    table_name="events",
    flat_meta_model=FlatMetaModel(
        fields=[
            ColumnField(name="event_time", data_type="DateTime"),
            ColumnField(name="user_id", data_type="UInt64"),
            ColumnField(name="event_type", data_type="String")
        ],
        partitioning_key="toYYYYMM(event_time)"
    ),
    load_strategy="append"
)

# Full table reference: analytics.events (schema not typically used)
```

### HDFS Example (with Hive)

```python
load_config = LoadConfig(
    target_storage_type=TargetStorageTypeRecommendation(
        storage_type="hdfs",
        explanation="Big data lake storage"
    ),
    target_storage_connection_string="hdfs://namenode:9002",
    database_name="analytics",  # Hive database
    schema_name="",  # Not used in HDFS/Hive
    table_name="events",  # Hive table
    nesting_metamodel=NestingMetaModel(
        data_structure={"event_data": "nested_json"},
        partitioning_key="date"
    ),
    hdfs_config=HDFSConfig(
        hdfs_path="/user/hive/warehouse/analytics.db/events",
        file_format="parquet",
        use_hive=True,
        hive_database="analytics",
        hive_table="events",
        partition_columns=["year", "month", "day"],
        partition_pattern="year={year}/month={month}/day={day}/",
        compression="snappy"
    ),
    load_strategy="incremental"
)

# Hive reference: analytics.events
# HDFS path: /user/hive/warehouse/analytics.db/events/year=2025/month=10/day=02/
```

### HDFS Example (raw files, no Hive)

```python
load_config = LoadConfig(
    target_storage_type=TargetStorageTypeRecommendation(
        storage_type="hdfs",
        explanation="Raw data lake storage"
    ),
    target_storage_connection_string="hdfs://namenode:9002",
    database_name="",  # Not used
    schema_name="",    # Not used
    table_name="",     # Not used (files, not tables)
    nesting_metamodel=NestingMetaModel(
        data_structure={"raw_events": "json"},
        partitioning_key="date"
    ),
    hdfs_config=HDFSConfig(
        hdfs_path="/data/raw/events",
        file_format="json",
        use_hive=False,
        partition_columns=["date"],
        partition_pattern="date={date}/",
        compression="gzip"
    ),
    load_strategy="append"
)

# HDFS path: /data/raw/events/date=2025-10-02/data_*.json.gz
```

---

## How DAGBuilder Should Use These Fields

### Current (Broken)

```python
# backend/builders/dag/builder.py:152-157
table_name = (
    load_config.flat_meta_model.fields[0].name  # ❌ WRONG!
    if load_config.flat_meta_model.fields
    else "target_table"
)
```

### Should Be

```python
# For PostgreSQL/ClickHouse
full_table_name = f"{load_config.database_name}.{load_config.schema_name}.{load_config.table_name}"

# For ClickHouse (often no schema)
if load_config.target_storage_type.storage_type == "clickhouse":
    full_table_name = f"{load_config.database_name}.{load_config.table_name}"

# For HDFS (use path instead)
if load_config.target_storage_type.storage_type == "hdfs":
    if load_config.hdfs_config.use_hive:
        full_table_name = f"{load_config.hdfs_config.hive_database}.{load_config.hdfs_config.hive_table}"
    else:
        full_table_name = load_config.hdfs_config.hdfs_path
```

---

## Action Items

### 1. Update LoadConfig Model

**File**: [`backend/models/load.py`](../models/load.py)

Add these fields:
```python
database_name: str = Field(..., description="Target database name")
schema_name: str = Field("public", description="Target schema name")
table_name: str = Field(..., description="Target table name")
hdfs_config: HDFSConfig | None = Field(None, description="HDFS-specific config")
```

### 2. Update LoadConfigBuilder

**File**: [`backend/builders/load/builder.py`](../builders/load/builder.py)

Update LLM prompt to generate these fields:
```python
system_prompt = """
...
- Database name (extract from connection string or specify explicitly)
- Schema name (e.g., 'public' for PostgreSQL, 'default' for ClickHouse)
- Table name (derived from user prompt or content)
- HDFS config if target is HDFS
...
"""
```

### 3. Update DAGBuilder

**File**: [`backend/builders/dag/builder.py`](../builders/dag/builder.py)

Remove the workaround and use explicit fields:
```python
# Instead of line 153-157
full_table_name = self._get_full_table_name(load_config)

def _get_full_table_name(self, load_config: LoadConfig) -> str:
    if load_config.target_storage_type.storage_type == "postgres":
        return f"{load_config.database_name}.{load_config.schema_name}.{load_config.table_name}"
    elif load_config.target_storage_type.storage_type == "clickhouse":
        return f"{load_config.database_name}.{load_config.table_name}"
    elif load_config.target_storage_type.storage_type == "hdfs":
        if load_config.hdfs_config and load_config.hdfs_config.use_hive:
            return f"{load_config.hdfs_config.hive_database}.{load_config.hdfs_config.hive_table}"
        return load_config.hdfs_config.hdfs_path
    return "unknown_table"
```

### 4. Update Templates

**Files**: 
- [`backend/builders/dag/templates/config_template.py.j2`](../builders/dag/templates/config_template.py.j2)
- [`backend/builders/dag/templates/functions_template.py.j2`](../builders/dag/templates/functions_template.py.j2)

Add variables:
```python
TARGET_DATABASE = "{{ load_config.database_name }}"
TARGET_SCHEMA = "{{ load_config.schema_name }}"
TARGET_TABLE = "{{ load_config.table_name }}"
FULL_TABLE_NAME = "{{ load_config.database_name }}.{{ load_config.schema_name }}.{{ load_config.table_name }}"
```

---

## Summary

**Current State**: ⚠️ LoadConfig is incomplete and uses workarounds

**What's Needed**:
- **PostgreSQL/ClickHouse**: `database_name`, `schema_name`, `table_name`
- **HDFS**: `hdfs_config` with path, format, Hive settings, partitioning

**Priority**: **HIGH** - This affects all load operations

**Reference Implementation**: See `backend/stuff/dag_generation/pipeline_config_models.py` for a better model structure.