# DAG Functions Implementation Plan

## Current Status

The generated DAG functions are **placeholder implementations** that don't actually connect to data sources or targets. This is why the DAG executes successfully but doesn't move any data.

### Evidence from Logs
```
[2025-10-02, 11:00:47 UTC] ✅ Извлечение завершено: 0 записей
[2025-10-02, 11:00:48 UTC] Получено записей для обработки: 0
[2025-10-02, 11:00:49 UTC] Получено записей для загрузки: 0
```

## Required Implementations

### 1. Extract Functions

#### 1.1 S3/MinIO Extraction
**File**: `backend/builders/dag/templates/functions_template.py.j2` (lines 44-72)

**Current**: Returns 0 records for `SOURCE_TYPE == "s3"`

**Need to implement**:
```python
import boto3
from botocore.client import Config

def extract_from_s3():
    """Extract data from S3/MinIO."""
    s3_client = boto3.client(
        's3',
        endpoint_url=SOURCE_PATH,  # e.g., http://minio:9000
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        config=Config(signature_version='s3v4')
    )
    
    # List objects in bucket
    response = s3_client.list_objects_v2(
        Bucket=S3_BUCKET,
        Prefix=S3_PREFIX
    )
    
    # Download and parse files
    for obj in response.get('Contents', []):
        file_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=obj['Key'])
        content = file_obj['Body'].read()
        
        # Parse based on CONTENT_TYPE (csv, json, xml)
        if CONTENT_TYPE == 'csv':
            data = parse_csv(content)
        elif CONTENT_TYPE == 'json':
            data = parse_json(content)
        elif CONTENT_TYPE == 'xml':
            data = parse_xml(content)
            
        extracted_data.extend(data)
    
    return extracted_data
```

**Dependencies needed**:
- `boto3` - AWS SDK for S3 operations
- `pandas` - For CSV parsing
- `xml.etree.ElementTree` or `lxml` - For XML parsing

#### 1.2 PostgreSQL Extraction
**Current**: Not implemented

**Need to implement**:
```python
import psycopg2
from psycopg2.extras import RealDictCursor

def extract_from_postgres():
    """Extract data from PostgreSQL."""
    conn = psycopg2.connect(SOURCE_PATH)  # connection string
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Execute query from SOURCE_QUERY or build from metadata
    query = SOURCE_QUERY if SOURCE_QUERY else f"SELECT * FROM {SOURCE_TABLE}"
    cursor.execute(query)
    
    # Fetch in batches
    while True:
        rows = cursor.fetchmany(BATCH_SIZE)
        if not rows:
            break
        extracted_data.extend([dict(row) for row in rows])
    
    cursor.close()
    conn.close()
    
    return extracted_data
```

**Dependencies needed**:
- `psycopg2-binary` - PostgreSQL adapter

#### 1.3 ClickHouse Extraction
**Current**: Not implemented

**Need to implement**:
```python
from clickhouse_driver import Client

def extract_from_clickhouse():
    """Extract data from ClickHouse."""
    # Parse connection string
    # clickhouse://user:pass@host:port/database
    client = Client.from_url(SOURCE_PATH)
    
    # Execute query
    query = SOURCE_QUERY if SOURCE_QUERY else f"SELECT * FROM {SOURCE_TABLE}"
    result = client.execute(query, with_column_types=True)
    
    # Convert to dict format
    columns = [col[0] for col in result[1]]
    rows = result[0]
    
    extracted_data = [dict(zip(columns, row)) for row in rows]
    
    return extracted_data
```

**Dependencies needed**:
- `clickhouse-driver` - ClickHouse Python driver

### 2. Load Functions

#### 2.1 PostgreSQL Loading
**File**: `backend/builders/dag/templates/functions_template.py.j2` (lines 134-189)

**Current**: Only logs, doesn't actually insert data

**Need to implement**:
```python
import psycopg2
from psycopg2.extras import execute_batch

def load_to_postgres(data):
    """Load data to PostgreSQL."""
    conn = psycopg2.connect(TARGET_CONNECTION)
    cursor = conn.cursor()
    
    # Execute DDL if exists
    if DDL_STATEMENTS:
        for statement in DDL_STATEMENTS.split(';'):
            if statement.strip():
                cursor.execute(statement)
        conn.commit()
    
    # Prepare insert statement
    if not data:
        logger.warning("No data to load")
        return 0
    
    columns = data[0].keys()
    table_name = f"{TARGET_SCHEMA}.{TARGET_TABLE}"
    
    if LOAD_STRATEGY == 'append':
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
        values = [[row[col] for col in columns] for row in data]
        execute_batch(cursor, query, values, page_size=BATCH_SIZE)
        
    elif LOAD_STRATEGY == 'upsert':
        # Implement UPSERT logic with ON CONFLICT
        conflict_cols = PRIMARY_KEY_COLUMNS  # from config
        query = f"""
            INSERT INTO {table_name} ({', '.join(columns)}) 
            VALUES ({', '.join(['%s'] * len(columns))})
            ON CONFLICT ({', '.join(conflict_cols)}) 
            DO UPDATE SET {', '.join([f'{col} = EXCLUDED.{col}' for col in columns if col not in conflict_cols])}
        """
        values = [[row[col] for col in columns] for row in data]
        execute_batch(cursor, query, values, page_size=BATCH_SIZE)
        
    elif LOAD_STRATEGY == 'full_refresh':
        # Truncate and insert
        cursor.execute(f"TRUNCATE TABLE {table_name}")
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
        values = [[row[col] for col in columns] for row in data]
        execute_batch(cursor, query, values, page_size=BATCH_SIZE)
    
    conn.commit()
    loaded_count = len(data)
    
    cursor.close()
    conn.close()
    
    return loaded_count
```

#### 2.2 ClickHouse Loading
**Current**: Not implemented

**Need to implement**:
```python
from clickhouse_driver import Client

def load_to_clickhouse(data):
    """Load data to ClickHouse."""
    client = Client.from_url(TARGET_CONNECTION)
    
    # Execute DDL if exists
    if DDL_STATEMENTS:
        for statement in DDL_STATEMENTS.split(';'):
            if statement.strip():
                client.execute(statement)
    
    # Prepare insert
    if not data:
        logger.warning("No data to load")
        return 0
    
    columns = data[0].keys()
    table_name = f"{TARGET_DATABASE}.{TARGET_TABLE}"
    
    if LOAD_STRATEGY == 'append':
        # ClickHouse batch insert
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES"
        client.execute(query, [tuple(row[col] for col in columns) for row in data])
        
    elif LOAD_STRATEGY == 'full_refresh':
        # Truncate and insert
        client.execute(f"TRUNCATE TABLE {table_name}")
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES"
        client.execute(query, [tuple(row[col] for col in columns) for row in data])
    
    return len(data)
```

### 3. Transform Functions

**Current status**: Mostly placeholder, but transforms are usually custom per-pipeline

**Enhancement needed**: Add common transformations:
- Type casting
- Date parsing
- String manipulation
- Null handling
- Data validation

## Implementation Strategy

### Phase 1: Core Extract/Load (Priority: HIGH)
1. Implement S3/MinIO extraction
2. Implement PostgreSQL loading
3. Test end-to-end: S3 → Transform → PostgreSQL

### Phase 2: Additional Sources (Priority: MEDIUM)
4. Implement PostgreSQL extraction
5. Implement ClickHouse extraction
6. Implement ClickHouse loading

### Phase 3: Advanced Features (Priority: LOW)
7. Implement transformation library
8. Add data quality checks
9. Add error handling and retries
10. Add monitoring and metrics

## Configuration Changes Needed

### Add to config template:
```python
# S3/MinIO credentials
S3_ACCESS_KEY = "{{ extract_config.s3_access_key if extract_config.source_metadata.source_type == 's3' else '' }}"
S3_SECRET_KEY = "{{ extract_config.s3_secret_key if extract_config.source_metadata.source_type == 's3' else '' }}"
S3_BUCKET = "{{ extract_config.s3_bucket if extract_config.source_metadata.source_type == 's3' else '' }}"
S3_PREFIX = "{{ extract_config.s3_prefix if extract_config.source_metadata.source_type == 's3' else '' }}"

# Source query (for DB sources)
SOURCE_QUERY = "{{ extract_config.source_query if extract_config.source_query else '' }}"
SOURCE_TABLE = "{{ extract_config.source_table if extract_config.source_table else '' }}"

# Primary keys for upsert
PRIMARY_KEY_COLUMNS = {{ load_config.indexing.primary_key if load_config.indexing.primary_key else [] }}
```

## Dependencies to Add

### Update `backend/builders/dag/templates/requirements.txt`:
```
apache-airflow==2.7.3
boto3>=1.28.0                # S3/MinIO
psycopg2-binary>=2.9.0       # PostgreSQL
clickhouse-driver>=0.2.6     # ClickHouse
pandas>=2.0.0                # Data manipulation
lxml>=4.9.0                  # XML parsing
```

## Testing Plan

1. **Unit tests** for each extraction function
2. **Integration tests** with test databases
3. **End-to-end tests** with sample data
4. **Performance tests** with large datasets

## Timeline Estimate

- Phase 1 (Core): 2-3 days
- Phase 2 (Additional): 2-3 days
- Phase 3 (Advanced): 3-5 days
- Testing: 2-3 days

**Total**: 9-14 days for full implementation

## Current Workaround

For testing the credential workflow and DAG generation:
1. Use folder-based extraction (already implemented)
2. Focus on testing the workflow split and credential forms
3. Actual data movement can be implemented incrementally

## Next Steps

1. Decide on implementation priority (which sources/targets first?)
2. Set up test environment with MinIO, PostgreSQL, ClickHouse
3. Create sample test data
4. Implement extract functions incrementally
5. Implement load functions incrementally
6. Add comprehensive error handling
7. Document usage examples