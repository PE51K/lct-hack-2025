# Generated Airflow DAGs Directory

This directory contains auto-generated Airflow DAG files organized by user and thread.

## Structure

```
backend/dags/
├── {user_id}/
│   └── {thread_id}/
│       ├── etl_{user_id}_{thread_id}.py           # Main DAG file
│       ├── etl_{user_id}_{thread_id}_functions.py # Task implementations
│       ├── etl_{user_id}_{thread_id}_config.py    # Configuration constants
│       └── __init__.py                             # Python package marker
```

## Usage

1. **Generation**: DAG files are automatically created when users submit ETL creation requests via the `/create_etl` API endpoint.

2. **Airflow Integration**: This directory is mounted as a Docker volume in the Airflow container:
   ```yaml
   volumes:
     - ./backend/dags:/opt/airflow/dags
   ```

3. **Auto-Discovery**: Airflow's scheduler scans this directory every 30 seconds and automatically registers new DAG files.

4. **Execution**: Once registered, DAGs can be triggered via:
   - Airflow Web UI: `http://localhost:8081`
   - Airflow REST API
   - Airflow CLI

## File Naming Convention

- **user_id**: Unique identifier for the user
- **thread_id**: Unique identifier for the conversation thread
- **DAG ID**: `etl_{user_id}_{thread_id}`

This ensures:
- ✅ No naming conflicts between users
- ✅ Version control per thread
- ✅ Easy cleanup and management
- ✅ Clear traceability

## Cleanup

Generated files are ephemeral and can be safely deleted. Consider implementing a cleanup policy for:
- Old or unused DAGs (e.g., > 30 days)
- Failed DAG generations
- Test/development DAGs

## Development

When developing, you can manually place test DAG files here to verify Airflow integration.

**Note**: All generated files are gitignored to avoid committing user-specific pipelines.