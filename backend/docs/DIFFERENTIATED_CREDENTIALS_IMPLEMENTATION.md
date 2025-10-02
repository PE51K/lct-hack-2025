# Differentiated Credentials Implementation

## Overview

This document describes the implementation of type-safe, differentiated credentials for target databases in the ETL DAG creation workflow.

## Problem Statement

Previously, the `CreateDAGRequest` model used a generic `dict[str, Any]` for `target_credentials`, which:
- Lacked type safety
- Didn't provide clear field validation
- Made it unclear what credentials were needed for each target type
- Could lead to runtime errors from missing or incorrect fields

## Solution

Created specific credential models for each target storage type with proper validation and documentation.

## Implementation Details

### 1. New Credential Models

Created three specialized credential models in [`backend/models/app/create_dag.py`](../models/app/create_dag.py):

#### PostgresCredentials
```python
class PostgresCredentials(BaseModel):
    """PostgreSQL database credentials."""
    host: str
    port: int = 5432
    username: str
    password: str
    database: str
    schema: str = "public"
```

#### ClickHouseCredentials
```python
class ClickHouseCredentials(BaseModel):
    """ClickHouse database credentials."""
    host: str
    port: int = 8123
    username: str
    password: str
    database: str
```

#### HDFSCredentials
```python
class HDFSCredentials(BaseModel):
    """HDFS storage credentials."""
    namenode_host: str
    namenode_port: int = 9870
    user: str
    base_path: str
    authentication: str = "simple"
```

### 2. Updated CreateDAGRequest

Changed from:
```python
target_credentials: dict[str, Any]
```

To:
```python
target_credentials: PostgresCredentials | ClickHouseCredentials | HDFSCredentials
```

This provides:
- **Type safety**: FastAPI/Pydantic validates the correct model
- **Auto-documentation**: OpenAPI schema shows exact fields needed
- **IDE support**: Better autocomplete and type hints
- **Runtime validation**: Automatic field validation

### 3. Updated Connection String Builder

Modified [`_update_connection_string()`](../app/routers/create_dag.py) in `create_dag.py`:

**Before:**
```python
def _update_connection_string(load_config: LoadConfig, credentials: dict) -> LoadConfig:
    # Generic dict access with potential KeyErrors
    connection_string = f"postgresql://{credentials['username']}:{credentials['password']}..."
```

**After:**
```python
def _update_connection_string(
    load_config: LoadConfig,
    credentials: PostgresCredentials | ClickHouseCredentials | HDFSCredentials,
) -> LoadConfig:
    if isinstance(credentials, PostgresCredentials):
        connection_string = f"postgresql://{credentials.username}:{credentials.password}..."
        load_config.schema_name = credentials.schema
    elif isinstance(credentials, ClickHouseCredentials):
        # ClickHouse-specific logic
    elif isinstance(credentials, HDFSCredentials):
        # HDFS-specific logic
```

**Improvements:**
- Type-safe attribute access (no dict key errors)
- Explicit type checking with `isinstance()`
- Proper handling of target-specific fields (e.g., `schema` for PostgreSQL)
- Raises `ValueError` for unsupported types instead of failing silently

### 4. Updated Credentials Form Generator

Enhanced [`_generate_credentials_form()`](../app/routers/create_etl.py) in `create_etl.py`:

Added full HDFS support:
```python
elif target_type == "hdfs":
    return CredentialsRequired(
        target_type="hdfs",
        fields=[
            CredentialField(name="namenode_host", label="HDFS NameNode Host", ...),
            CredentialField(name="namenode_port", label="NameNode Port", ...),
            CredentialField(name="user", label="HDFS User", ...),
            CredentialField(name="base_path", label="Base HDFS Path", ...),
            CredentialField(name="authentication", label="Authentication Method", ...),
        ],
    )
```

Added PostgreSQL schema field:
```python
CredentialField(
    name="schema",
    label="Schema Name",
    type="text",
    placeholder="public",
    default="public",
    required=False,
)
```

### 5. Updated Exports

Modified [`backend/models/app/__init__.py`](../models/app/__init__.py) to export new models:

```python
from .create_dag import (
    ClickHouseCredentials,
    CreateDAGRequest,
    CreateDAGResponse,
    HDFSCredentials,
    PostgresCredentials,
)
```

## Benefits

### Type Safety
- FastAPI validates incoming requests against correct credential model
- No runtime dict key errors
- Clear error messages when fields are missing or wrong type

### Developer Experience
- IDE autocomplete for credential fields
- Type hints throughout the codebase
- Clear documentation in OpenAPI schema

### Maintainability
- Easy to add new target types (create new credential model)
- Explicit field requirements for each target
- Centralized credential definitions

### User Experience
- Frontend gets exact field specifications via `/create_etl` response
- Clear validation errors if credentials are incorrect
- Target-specific field names (e.g., "NameNode Host" for HDFS)

## API Contract

### Frontend -> Backend Flow

1. **Call `/create_etl`** - AI recommends target type and returns configs
   ```json
   {
     "ids": {"user_id": "...", "thread_id": "..."},
     "processing_done": true,
     "processing_percentage_done": 80.0,
     "success": true,
     "extract_config": {...},
     "transform_config": {...},
     "load_config": {...},
     "ddl": {...},
     "credentials_required": {
       "target_type": "postgres",
       "fields": [
         {"name": "host", "label": "PostgreSQL Host", "type": "text", ...},
         {"name": "port", "label": "Port", "type": "number", ...},
         {"name": "username", "label": "Username", "type": "text", ...},
         {"name": "password", "label": "Password", "type": "password", ...},
         {"name": "database", "label": "Database Name", "type": "text", ...},
         {"name": "schema", "label": "Schema Name", "type": "text", ...}
       ]
     },
     "next_step": "create_dag"
   }
   ```

2. **Frontend stores configs and user fills form**, then calls `/create_dag`
   ```json
   {
     "ids": {"user_id": "...", "thread_id": "..."},
     "target_credentials": {
       "host": "postgres.example.com",
       "port": 5432,
       "username": "etl_user",
       "password": "secure_password",
       "database": "analytics",
       "schema": "public"
     },
     "extract_config": {...},
     "transform_config": {...},
     "load_config": {...},
     "ddl": {...}
   }
   ```

3. **Backend validates** credentials match target type and creates DAG files

## Connection String Formats

### PostgreSQL
```
postgresql://{username}:{password}@{host}:{port}/{database}
```
Additional: `schema_name` field in LoadConfig

### ClickHouse
```
clickhouse://{username}:{password}@{host}:{port}/{database}
```

### HDFS
```
hdfs://{namenode_host}:{namenode_port}{base_path}
```

## State Management

**No server-side session storage required.** The frontend is responsible for:
- Storing configs received from `/create_etl`
- Sending them back with credentials in `/create_dag` request

This approach:
- Eliminates need for temp file storage
- Makes backend stateless (easier to scale)
- Simplifies error recovery (user can retry with same data)
- Reduces server-side complexity

## Files Modified

1. [`backend/models/app/create_dag.py`](../models/app/create_dag.py) - Added credential models and config fields to request
2. [`backend/app/routers/create_dag.py`](../app/routers/create_dag.py) - Updated to receive configs from request instead of loading from disk
3. [`backend/app/routers/create_etl.py`](../app/routers/create_etl.py) - Removed temp file storage, enhanced credentials form
4. [`backend/models/app/__init__.py`](../models/app/__init__.py) - Exported new models
5. [`backend/app/routers/__init__.py`](../app/routers/__init__.py) - Exported create_dag_router
6. [`backend/app/app.py`](../app/app.py) - Registered create_dag_router

## Testing Recommendations

1. **Unit Tests**: Test each credential model with valid/invalid data
2. **Integration Tests**: Test `/create_dag` with each credential type
3. **Type Tests**: Verify FastAPI validation catches wrong credential types
4. **Connection Tests**: Test connection string generation for each target

## Future Enhancements

1. Add more target types (e.g., Kafka, S3, MongoDB)
2. Add credential validation (test connection before DAG creation)
3. Add credential encryption/secure storage
4. Add support for credential providers (AWS Secrets Manager, etc.)