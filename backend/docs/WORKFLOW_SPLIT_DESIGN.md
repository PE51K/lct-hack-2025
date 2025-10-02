# Workflow Split Design: create_etl + create_dag

**Date**: 2025-10-02  
**Status**: 🎯 **Design Proposal**

---

## Problem Statement

Currently, users must provide target database credentials upfront in their prompt. This is not optimal because:
1. User may not know which DB type is best for their data
2. AI can make better recommendations based on data characteristics
3. Mixing business logic (what to do) with technical details (credentials) in one prompt

---

## Proposed Solution

**Split the workflow into 2 steps:**

### Step 1: AI Analysis & Recommendation
**Endpoint**: `POST /create_etl` (modified)
- User provides only source info and transformation requirements
- AI analyzes data and recommends target DB type
- Returns configs WITHOUT creating DAG files
- **Stops before DAG generation**

### Step 2: User Confirms & Provides Credentials
**Endpoint**: `POST /create_dag` (NEW)
- User reviews AI recommendation
- User provides target DB credentials
- System creates DAG files and finalizes setup

---

## Detailed Workflow Design

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant API
    participant AI
    participant DAGBuilder
    participant FileGen
    
    User->>UI: 1. Enter source info only
    UI->>API: POST /create_etl (no target creds)
    
    API->>AI: Extract source data
    AI-->>API: ExtractConfig
    
    API->>AI: Recommend target & generate LoadConfig
    Note over AI: AI decides: PostgreSQL, ClickHouse, or HDFS
    AI-->>API: LoadConfig (with placeholder connection)
    
    API->>AI: Generate TransformConfig
    AI-->>API: TransformConfig
    
    API->>AI: Generate DDL
    AI-->>API: DDL
    
    Note over API: STOP HERE - Don't create DAG yet
    
    API-->>UI: Return configs + recommendation
    
    UI->>User: 2. Show AI recommendation
    Note over User: Reviews: "AI recommends ClickHouse"
    
    UI->>User: 3. Request credentials form
    User->>UI: Enter target DB credentials
    
    UI->>API: POST /create_dag (with credentials)
    
    API->>API: Update LoadConfig with real credentials
    
    API->>DAGBuilder: Create DAG model
    DAGBuilder-->>API: DAG
    
    API->>FileGen: Generate DAG files
    FileGen-->>API: File paths
    
    API-->>UI: DAG created successfully
    UI->>User: Show success + next steps
```

---

## API Changes

### 1. Modified: `/create_etl`

**Current behavior**: Creates everything including DAG files  
**New behavior**: Stops after generating configs, before DAG creation

#### Request (unchanged):
```json
POST /create_etl
{
  "ids": {
    "user_id": "user_123",
    "thread_id": "thread_456"
  },
  "user_prompt": "Extract from PostgreSQL table employees, transform and analyze"
}
```

#### Response (NEW format):
```json
{
  "ids": {"user_id": "user_123", "thread_id": "thread_456"},
  "processing_done": true,
  "processing_percentage_done": 80.0,  // Stops at 80%, not 100%
  "processing_message": "Configuration complete. Please provide target database credentials.",
  "success": true,
  
  "extract_config": { ... },
  "transform_config": { ... },
  "load_config": {
    "target_storage_type": {
      "storage_type": "clickhouse",
      "explanation": "Recommended for analytics workload with high query volume"
    },
    "target_storage_connection_string": "clickhouse://PLACEHOLDER",  // Placeholder
    "database_name": "analytics",
    "schema_name": "default",
    "table_name": "employees_processed"
    // ... other fields
  },
  "ddl": { ... },
  
  // NEW FIELD: What credentials are needed
  "credentials_required": {
    "target_type": "clickhouse",
    "fields": [
      {
        "name": "host",
        "label": "ClickHouse Host",
        "type": "text",
        "placeholder": "localhost",
        "required": true
      },
      {
        "name": "port",
        "label": "Port",
        "type": "number",
        "placeholder": "8123",
        "default": 8123,
        "required": true
      },
      {
        "name": "username",
        "label": "Username",
        "type": "text",
        "placeholder": "default",
        "required": true
      },
      {
        "name": "password",
        "label": "Password",
        "type": "password",
        "required": true
      },
      {
        "name": "database",
        "label": "Database Name",
        "type": "text",
        "default": "analytics",
        "required": true
      }
    ]
  },
  
  // NO dag field yet - DAG not created
  "dag": null,
  "next_step": "create_dag"
}
```

### 2. NEW: `/create_dag`

**Purpose**: Finalize ETL setup with user-provided credentials

#### Request:
```json
POST /create_dag
{
  "ids": {
    "user_id": "user_123",
    "thread_id": "thread_456"
  },
  "target_credentials": {
    "host": "clickhouse.example.com",
    "port": 8123,
    "username": "etl_user",
    "password": "secure_password",
    "database": "analytics"
  }
}
```

#### Response:
```json
{
  "ids": {"user_id": "user_123", "thread_id": "thread_456"},
  "processing_done": true,
  "processing_percentage_done": 100.0,
  "processing_message": "DAG created successfully!",
  "success": true,
  
  "dag": {
    "dag_id": "etl_user_123_thread_456",
    "generated_files": {
      "dag_file": "backend/dags/user_123/thread_456/etl_user_123_thread_456.py",
      "functions_file": "...",
      "config_file": "..."
    },
    "dag_file_path": "..."
  },
  
  "updated_load_config": {
    "target_storage_connection_string": "clickhouse://etl_user:***@clickhouse.example.com:8123/analytics",
    // ... other fields updated with real credentials
  }
}
```

---

## Implementation Details

### Modified: `backend/app/routers/create_etl.py`

```python
@create_router.post("/create_etl")
async def create_etl(request: CreateETLRequest) -> StreamingResponse:
    """Create ETL configuration (WITHOUT DAG files)."""
    
    async def create(request: CreateETLRequest) -> AsyncGenerator[str, None]:
        try:
            # Step 1-5: Same as before (Extract, Load, DDL, Transform)
            # ... (20% - 80%)
            
            # Step 6: Determine credentials needed (NEW)
            yield CreateETLResponse(
                ids=request.ids,
                processing_done=False,
                processing_percentage_done=85.0,
                processing_message="Preparing credentials form...",
                success=True,
            ).model_dump_json() + "\n"
            
            credentials_required = _generate_credentials_form(load_config.target_storage_type.storage_type)
            
            # STOP HERE - Don't create DAG yet
            
            # Final response with configs but NO DAG
            yield CreateETLResponse(
                ids=request.ids,
                processing_done=True,
                processing_percentage_done=80.0,  # Not 100%
                processing_message="Configuration complete. Please provide target credentials.",
                success=True,
                extract_config=extract_config,
                transform_config=transform_config,
                load_config=load_config,
                ddl=ddl,
                credentials_required=credentials_required,  # NEW
                dag=None,  # No DAG yet
                next_step="create_dag",  # NEW
            ).model_dump_json() + "\n"
            
        except Exception as e:
            # ... error handling
            
    return StreamingResponse(create(request), media_type="application/x-ndjson")


def _generate_credentials_form(target_type: str) -> dict:
    """Generate credentials form based on target DB type."""
    if target_type == "postgres":
        return {
            "target_type": "postgres",
            "fields": [
                {"name": "host", "label": "PostgreSQL Host", "type": "text", "required": True},
                {"name": "port", "label": "Port", "type": "number", "default": 5432, "required": True},
                {"name": "username", "label": "Username", "type": "text", "required": True},
                {"name": "password", "label": "Password", "type": "password", "required": True},
                {"name": "database", "label": "Database", "type": "text", "required": True},
            ]
        }
    elif target_type == "clickhouse":
        return {
            "target_type": "clickhouse",
            "fields": [
                {"name": "host", "label": "ClickHouse Host", "type": "text", "required": True},
                {"name": "port", "label": "HTTP Port", "type": "number", "default": 8123, "required": True},
                {"name": "username", "label": "Username", "type": "text", "default": "default", "required": True},
                {"name": "password", "label": "Password", "type": "password", "required": False},
                {"name": "database", "label": "Database", "type": "text", "required": True},
            ]
        }
    # ... other target types
```

### NEW: `backend/app/routers/create_dag.py`

```python
"""Router for DAG file generation after credentials provided."""

from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

from builders.dag import AirflowFileGenerator, DAGBuilder
from models.app import CreateDAGRequest, CreateDAGResponse

create_dag_router = APIRouter()


@create_dag_router.post("/create_dag")
async def create_dag(request: CreateDAGRequest) -> CreateDAGResponse:
    """
    Create DAG files after user provides target credentials.
    
    This endpoint is called after /create_etl when user provides credentials.
    """
    try:
        # 1. Load saved configs from previous step
        configs = await _load_saved_configs(request.ids.user_id, request.ids.thread_id)
        
        if not configs:
            raise HTTPException(
                status_code=404,
                detail="ETL configuration not found. Please run /create_etl first."
            )
        
        extract_config = configs["extract_config"]
        transform_config = configs["transform_config"]
        load_config = configs["load_config"]
        ddl = configs["ddl"]
        
        # 2. Update LoadConfig with real credentials
        updated_load_config = _update_connection_string(
            load_config,
            request.target_credentials
        )
        
        # 3. Create DAG model
        dag_builder = DAGBuilder()
        dag = await dag_builder(
            extract_config,
            transform_config,
            updated_load_config,
            ddl
        )
        
        # 4. Generate DAG files
        file_generator = AirflowFileGenerator()
        generated_files = await file_generator.generate_dag_files(
            dag=dag,
            extract_config=extract_config,
            transform_config=transform_config,
            load_config=updated_load_config,
            ddl=ddl,
            user_id=request.ids.user_id,
            thread_id=request.ids.thread_id,
        )
        
        dag.generated_files = generated_files
        dag.dag_file_path = generated_files.get("dag_file")
        
        # 5. Save final configs with credentials (optional, for audit)
        await _save_final_configs(
            request.ids.user_id,
            request.ids.thread_id,
            {
                "extract_config": extract_config,
                "transform_config": transform_config,
                "load_config": updated_load_config,  # With real credentials
                "ddl": ddl,
                "dag": dag
            }
        )
        
        return CreateDAGResponse(
            ids=request.ids,
            processing_done=True,
            processing_percentage_done=100.0,
            processing_message="DAG created successfully!",
            success=True,
            dag=dag,
            updated_load_config=updated_load_config,
        )
        
    except Exception as e:
        logger.error(f"Error creating DAG: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


def _update_connection_string(load_config: LoadConfig, credentials: dict) -> LoadConfig:
    """Update LoadConfig with user-provided credentials."""
    target_type = load_config.target_storage_type.storage_type
    
    if target_type == "postgres":
        connection_string = (
            f"postgresql://{credentials['username']}:{credentials['password']}"
            f"@{credentials['host']}:{credentials['port']}/{credentials['database']}"
        )
    elif target_type == "clickhouse":
        password_part = f":{credentials['password']}" if credentials.get('password') else ""
        connection_string = (
            f"clickhouse://{credentials['username']}{password_part}"
            f"@{credentials['host']}:{credentials['port']}/{credentials['database']}"
        )
    else:
        connection_string = load_config.target_storage_connection_string
    
    # Create updated config
    load_config.target_storage_connection_string = connection_string
    load_config.database_name = credentials.get('database', load_config.database_name)
    
    return load_config


async def _load_saved_configs(user_id: str, thread_id: str) -> dict | None:
    """Load saved configs from previous /create_etl call."""
    config_path = Path(f"temp/configs/{user_id}/{thread_id}/etl_config.json")
    
    if not config_path.exists():
        return None
    
    with open(config_path, 'r') as f:
        return json.load(f)


async def _save_final_configs(user_id: str, thread_id: str, configs: dict):
    """Save final configs with credentials for audit."""
    config_path = Path(f"temp/configs/{user_id}/{thread_id}")
    config_path.mkdir(parents=True, exist_ok=True)
    
    with open(config_path / "final_config.json", 'w') as f:
        json.dump(configs, f, default=str, indent=2)
```

---

## New Models

### `backend/models/app/create_etl.py` (modified)

```python
class CredentialField(BaseModel):
    """Field definition for credentials form."""
    name: str
    label: str
    type: str  # "text", "password", "number"
    placeholder: str | None = None
    default: Any | None = None
    required: bool = True


class CredentialsRequired(BaseModel):
    """Credentials requirement specification."""
    target_type: str
    fields: list[CredentialField]


class CreateETLResponse(BaseModel):
    # ... existing fields ...
    
    # NEW FIELDS:
    credentials_required: CredentialsRequired | None = None
    next_step: str | None = None  # "create_dag"
```

### `backend/models/app/create_dag.py` (NEW)

```python
"""Models for create_dag endpoint."""

from pydantic import BaseModel, Field
from models.app.ids import Ids
from models.dag import DAG
from models.load import LoadConfig


class CreateDAGRequest(BaseModel):
    """Request for creating DAG after credentials provided."""
    
    ids: Ids = Field(..., description="User and thread identifiers")
    target_credentials: dict[str, Any] = Field(
        ...,
        description="Target database credentials",
        examples=[{
            "host": "clickhouse.example.com",
            "port": 8123,
            "username": "etl_user",
            "password": "secure_password",
            "database": "analytics"
        }]
    )


class CreateDAGResponse(BaseModel):
    """Response after DAG creation."""
    
    ids: Ids
    processing_done: bool
    processing_percentage_done: float
    processing_message: str
    success: bool
    dag: DAG | None = None
    updated_load_config: LoadConfig | None = None
    error_message: str | None = None
```

---

## Frontend Changes (UI)

### Step 1: Initial Form
```typescript
// User enters ONLY source info
const prompt = "Extract from PostgreSQL table employees and transform";

const response = await api.post('/create_etl', {
  ids: { user_id, thread_id },
  user_prompt: prompt
});
```

### Step 2: Show AI Recommendation
```typescript
// Display AI recommendation
if (response.credentials_required) {
  showRecommendation(response.load_config.target_storage_type.explanation);
  // "AI recommends ClickHouse for high-volume analytics workload"
  
  // Show credentials form
  const form = generateCredentialsForm(response.credentials_required.fields);
  showCredentialsForm(form);
}
```

### Step 3: Submit Credentials
```typescript
// User fills out credentials
const credentials = {
  host: "clickhouse.prod.company.com",
  port: 8123,
  username: "etl_service",
  password: userInput.password,
  database: "analytics"
};

// Call create_dag
const dagResponse = await api.post('/create_dag', {
  ids: { user_id, thread_id },
  target_credentials: credentials
});

// Show success
if (dagResponse.success) {
  showSuccess("DAG created successfully!");
  showNextSteps(dagResponse.dag.dag_file_path);
}
```

---

## Benefits

### User Experience
✅ Simplified initial prompt (no credentials needed upfront)  
✅ AI provides expert recommendation  
✅ Clear separation: business logic vs technical details  
✅ User reviews before committing credentials  

### Security
✅ Credentials only provided when needed  
✅ No credentials in initial prompt (which might be logged)  
✅ Credentials not stored in intermediate configs  

### Flexibility
✅ User can override AI recommendation  
✅ Can test different target DBs easily  
✅ Clear decision point in workflow  

---

## Migration Path

### Phase 1: Add new endpoint (backward compatible)
- Keep old `/create_etl` working
- Add new `/create_dag` endpoint
- Frontend can use either flow

### Phase 2: Update frontend
- Implement new 2-step flow in UI
- Keep old flow as fallback

### Phase 3: Deprecate old flow
- Eventually remove old behavior
- All users on new flow

---

## File Structure

```
backend/
├── app/
│   └── routers/
│       ├── create_etl.py          # Modified: stops at 80%
│       ├── create_dag.py          # NEW: finalizes with credentials
│       └── __init__.py            # Updated: add create_dag_router
├── models/
│   └── app/
│       ├── create_etl.py          # Modified: add credentials_required
│       └── create_dag.py          # NEW: CreateDAGRequest/Response
└── temp/
    └── configs/                    # NEW: temp storage for intermediate configs
        └── {user_id}/
            └── {thread_id}/
                ├── etl_config.json      # After create_etl
                └── final_config.json    # After create_dag
```

---

## Summary

**Old Flow**:
```
User prompt (with all info) → AI → DAG files → Done
```

**New Flow**:
```
User prompt (source only) → AI → Recommendation → User provides creds → DAG files → Done
```

This design provides a better user experience, improves security, and gives users more control over the ETL setup process.