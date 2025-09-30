"""
Configuration file for Mock PostgreSQL Pipeline

Содержит все константы и настройки для DAG.
"""

# DAG Configuration
DAG_ID = "etl_mock_postgresql_pipeline"
DAG_NAME = "Mock PostgreSQL Pipeline"
DAG_OWNER = "test_user"

# Source Configuration
SOURCE_PATH = "postgres://mock_user:mock_pass@localhost:5432/mock_db"
SOURCE_TYPE = "postgres"
CONTENT_TYPE = "table"

# Processing Configuration  
BATCH_SIZE = 1000
PARALLEL_WORKERS = 1
MAX_DATA_SIZE_BYTES = 1073741824

# Target Configuration
TARGET_STORAGE_TYPE = "postgres"
TARGET_CONNECTION = "postgresql://localhost:5432/dwh"
TARGET_DATABASE = "dwh"
TARGET_SCHEMA = "public"
TARGET_TABLE = "Mock PostgreSQL Pipeline_data"

# Load Configuration
LOAD_STRATEGY = "incremental"
LOAD_BATCH_SIZE = 10000
CONCURRENT_CONNECTIONS = 5

# Processing Directories
TEMP_DIR = "/tmp/etl_processing/etl_mock_postgresql_pipeline"
LOG_DIR = "/var/log/airflow/dags/etl_mock_postgresql_pipeline"

# Resource Limits
CPU_CORES = 4.0
MEMORY_MB = 3972
EXECUTION_TIMEOUT_HOURS = 2

# Quality Thresholds
MIN_COMPLETENESS = 0.95
MIN_ACCURACY = 0.98
MAX_DUPLICATES_PCT = 0.05

# Notification Settings
EMAIL_ON_SUCCESS = False
EMAIL_ON_FAILURE = True
NOTIFICATION_EMAILS = ['test_user@company.com']

# Performance Settings (from AI Recommendations)
# AI Рекомендация: Увеличение ресурсов для больших объемов данных
ENABLE_PARALLEL_PROCESSING = True
