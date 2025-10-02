# Real ETL Implementation - Complete Guide

## Overview

The DAG generation system now includes **real, working implementations** of extraction, transformation, and loading operations. Data will actually move from source to target.

## What Changed

### Before (Placeholder)
```python
def extract_data():
    return {"total_records": 0}  # Fake

def load_data():
    logger.info("Loading...")  # Just logs, no actual INSERT
```

### After (Real Implementation)
```python
def extract_data():
    import boto3
    s3 = boto3.client('s3', endpoint_url='http://minio:9000')
    files = s3.list_objects(Bucket='mybucket')
    data = parse_files(files)  # Real data
    return {"total_records": len(data), "data": data}

def load_data():
    import psycopg2
    conn = psycopg2.connect(connection_string)
    cursor.execute("INSERT INTO table VALUES (%s, %s)", data)
    conn.commit()  # Real database writes
```

## Supported Sources (Extract)

### 1. S3/MinIO
**Configuration:**
- `SOURCE_TYPE`: `"s3"`
- `SOURCE_PATH`: S3 endpoint URL (e.g., `"http://minio:9000"`)
- `CONTENT_TYPE`: `"csv"`, `"json"`, or `"xml"`

**Environment Variables Required:**
```bash
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET=etl-data
S3_PREFIX=data/
```

**Features:**
- Lists all objects in bucket with prefix
- Downloads files
- Parses CSV, JSON, XML formats
- Returns structured data

### 2. PostgreSQL
**Configuration:**
- `SOURCE_TYPE`: `"postgres"`
- `SOURCE_PATH`: Connection string (`"postgresql://user:pass@host:port/db"`)

**Environment Variables (optional):**
```bash
SOURCE_QUERY=SELECT * FROM employees WHERE active = true
SOURCE_TABLE=employees  # Used if SOURCE_QUERY not provided
```

**Features:**
- Executes custom SQL queries
- Fetches data in batches
- Returns all rows as dictionaries

### 3. ClickHouse
**Configuration:**
- `SOURCE_TYPE`: `"clickhouse"`
- `SOURCE_PATH`: Connection string (`"clickhouse://user:pass@host:port/db"`)

**Environment Variables (optional):**
```bash
SOURCE_QUERY=SELECT * FROM events WHERE date >= today()
SOURCE_TABLE=events  # Used if SOURCE_QUERY not provided
```

**Features:**
- Executes ClickHouse SQL
- Efficient column-oriented extraction
- Returns structured data

### 4. Local Folder
**Configuration:**
- `SOURCE_TYPE`: `"folder"`
- `SOURCE_PATH`: Local directory path
- `CONTENT_TYPE`: `"csv"`, `"json"`, or `"xml"`

**Features:**
- Scans directory for matching files
- Parses all files
- Combines into single dataset

## Transformation Engine

### Supported Transformation Types

#### 1. Identity (No Change)
```python
{
    "rule_name": "pass_through",
    "transformation_type": "identity"
}
```

#### 2. Rename Field
```python
{
    "rule_name": "rename_employee_id",
    "transformation_type": "rename",
    "source_field": "emp_id",
    "target_field": "employee_id"
}
```

#### 3. Type Casting
```python
{
    "rule_name": "cast_salary",
    "transformation_type": "cast",
    "target_field": "salary",
    "cast_to": "float"  # int, float, str, bool
}
```

#### 4. Expression Evaluation
```python
{
    "rule_name": "calculate_age",
    "transformation_type": "expression",
    "target_field": "age",
    "expression": "(datetime.now().year - row['birth_year'])"
}
```

#### 5. Default Values
```python
{
    "rule_name": "default_status",
    "transformation_type": "default",
    "target_field": "status",
    "default_value": "active"
}
```

#### 6. Filter Rows
```python
{
    "rule_name": "filter_active",
    "transformation_type": "filter",
    "expression": "row['status'] == 'active'"
}
```

### Processing Modes

- **`batch`** (default): Process all records together
- **`strict`**: Remove rows with any null values
- **`streaming`**: Process one record at a time (future)

## Supported Targets (Load)

### 1. PostgreSQL
**Configuration:**
- `TARGET_STORAGE_TYPE`: `"postgres"`
- `TARGET_CONNECTION`: `"postgresql://user:pass@host:port/db"`
- `TARGET_SCHEMA`: Schema name (default: `"public"`)
- `TARGET_TABLE`: Table name

**Load Strategies:**

#### APPEND
```python
LOAD_STRATEGY = "append"
```
- Inserts all rows
- No duplicate checking
- Fastest strategy

#### UPSERT
```python
LOAD_STRATEGY = "upsert"
PRIMARY_KEY_COLUMNS = ["employee_id"]
```
- INSERT if new, UPDATE if exists
- Requires primary key configuration
- Uses PostgreSQL `ON CONFLICT ... DO UPDATE`

#### FULL_REFRESH
```python
LOAD_STRATEGY = "full_refresh"
```
- Truncates table first
- Then inserts all data
- Complete table replacement

#### INCREMENTAL
```python
LOAD_STRATEGY = "incremental"
```
- Appends only new records
- Similar to APPEND but with timestamp checking

**DDL Support:**
- Automatically executes CREATE TABLE statements
- Creates indexes if specified
- Sets up constraints

### 2. ClickHouse
**Configuration:**
- `TARGET_STORAGE_TYPE`: `"clickhouse"`
- `TARGET_CONNECTION`: `"clickhouse://user:pass@host:port/db"`
- `TARGET_DATABASE`: Database name
- `TARGET_TABLE`: Table name

**Load Strategies:**

#### APPEND
- Inserts all rows
- Default for ClickHouse

#### FULL_REFRESH
- Truncates table
- Inserts all data

**Note:** ClickHouse doesn't support UPSERT directly. Use `ReplacingMergeTree` engine for deduplication.

## Dependencies

The following Python packages are required in the Airflow environment:

```txt
apache-airflow==2.7.3
boto3>=1.28.0                # S3/MinIO
psycopg2-binary>=2.9.0       # PostgreSQL
clickhouse-driver>=0.2.6     # ClickHouse
pandas>=2.0.0                # Data manipulation
lxml>=4.9.0                  # XML parsing
```

## Example: Complete ETL Pipeline

### Scenario
Extract CSV files from MinIO → Transform → Load to PostgreSQL

### 1. Source Configuration (MinIO)
```python
SOURCE_TYPE = "s3"
SOURCE_PATH = "http://minio:9000"
CONTENT_TYPE = "csv"
BATCH_SIZE = 1000

# Environment:
AWS_ACCESS_KEY_ID = "minioadmin"
AWS_SECRET_ACCESS_KEY = "minioadmin"
S3_BUCKET = "employee-data"
S3_PREFIX = "2025/01/"
```

### 2. Transformation Rules
```python
TRANSFORMATION_RULES = [
    {
        "rule_name": "rename_id",
        "transformation_type": "rename",
        "source_field": "emp_id",
        "target_field": "employee_id"
    },
    {
        "rule_name": "cast_salary",
        "transformation_type": "cast",
        "target_field": "salary",
        "cast_to": "float"
    },
    {
        "rule_name": "filter_active",
        "transformation_type": "filter",
        "expression": "row.get('status') == 'active'"
    }
]
```

### 3. Target Configuration (PostgreSQL)
```python
TARGET_STORAGE_TYPE = "postgres"
TARGET_CONNECTION = "postgresql://user:pass@postgres:5432/hr_db"
TARGET_DATABASE = "hr_db"
TARGET_SCHEMA = "public"
TARGET_TABLE = "employees"
LOAD_STRATEGY = "upsert"
PRIMARY_KEY_COLUMNS = ["employee_id"]
```

### 4. Execution Flow
```
1. Extract Task:
   - Connects to MinIO at http://minio:9000
   - Lists objects in bucket "employee-data" with prefix "2025/01/"
   - Downloads CSV files
   - Parses into 1000 records
   - Returns: {"total_records": 1000, "data": [...]}

2. Transform Task:
   - Receives 1000 records
   - Renames emp_id → employee_id
   - Casts salary to float
   - Filters only active employees → 850 records remain
   - Returns: {"transformed_records": 850, "data": [...]}

3. Load Task:
   - Receives 850 records
   - Connects to PostgreSQL
   - Executes CREATE TABLE if needed
   - Uses UPSERT strategy with employee_id as key
   - INSERTs new records, UPDATEs existing
   - Returns: {"loaded_records": 850}
```

## Testing

### 1. Test Extract
```bash
# Check Airflow logs for extract_data task
# Should see:
# "📥 Извлечение из S3/MinIO"
# "Извлечено записей: 1000"
```

### 2. Test Transform
```bash
# Check transform_data task logs
# Should see:
# "🔄 Начало трансформации данных"
# "Применение правила 'rename_id'"
# "После правила 'filter_active': 850 записей"
```

### 3. Test Load
```bash
# Check load_data task logs
# Should see:
# "📤 Загрузка в PostgreSQL"
# "Стратегия: UPSERT"
# "✅ Загружено записей: 850"

# Verify in database:
psql -U user -d hr_db -c "SELECT COUNT(*) FROM employees;"
# Should show 850 rows
```

## Troubleshooting

### Extract Issues

**Problem**: "No objects found in bucket"
- Check S3_BUCKET and S3_PREFIX environment variables
- Verify MinIO credentials
- Use MinIO console to check bucket contents

**Problem**: "Connection refused to S3 endpoint"
- Check SOURCE_PATH is correct
- Verify MinIO is running: `docker ps | grep minio`
- Check network connectivity between Airflow and MinIO

### Transform Issues

**Problem**: "Expression eval failed"
- Check transformation expression syntax
- Ensure all fields referenced exist in data
- Use simpler expressions for testing

### Load Issues

**Problem**: "Table does not exist"
- Verify DDL statements are in config
- Check TARGET_DATABASE, TARGET_SCHEMA, TARGET_TABLE
- Manually create table for testing

**Problem**: "UPSERT conflict error"
- Verify PRIMARY_KEY_COLUMNS are correct
- Ensure primary key exists in table
- Check data has no nulls in key columns

## Performance Tips

1. **Batch Size**: Adjust `BATCH_SIZE` and `LOAD_BATCH_SIZE` based on data volume
2. **Parallel Workers**: Increase for large datasets
3. **Indexing**: Add indexes on frequently queried columns
4. **Compression**: Enable for large text fields
5. **Partitioning**: Use for time-series data

## Security

- **Never commit credentials** to git
- Use Airflow **Variables** or **Connections** for sensitive data
- Enable SSL/TLS for database connections in production
- Rotate credentials regularly
- Use read-only accounts for source extraction

## Next Steps

1. Generate a new DAG with the updated templates
2. Configure environment variables in Airflow
3. Run the DAG and monitor logs
4. Verify data in target database
5. Set up monitoring and alerts