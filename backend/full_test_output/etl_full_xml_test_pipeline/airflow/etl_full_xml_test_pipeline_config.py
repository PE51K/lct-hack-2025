"""
Configuration file for Full XML Test Pipeline

Содержит все константы и настройки для DAG.
"""

# DAG Configuration
DAG_ID = "etl_full_xml_test_pipeline"
DAG_NAME = "Full XML Test Pipeline"
DAG_OWNER = "test_user"

# Source Configuration
SOURCE_PATH = "file://d:/lct-hack-2025/backend/parsers/sample/XML/"
SOURCE_TYPE = "folder"
CONTENT_TYPE = "xml"

# Processing Configuration
BATCH_SIZE = 1000
PARALLEL_WORKERS = 2
MAX_DATA_SIZE_BYTES = 1073741824

# Target Configuration
TARGET_STORAGE_TYPE = "postgres"
TARGET_CONNECTION = "postgresql://localhost:5432/dwh"
TARGET_DATABASE = "dwh"
TARGET_SCHEMA = "public"
TARGET_TABLE = "Full XML Test Pipeline_data"

# Load Configuration
LOAD_STRATEGY = "full_refresh"
LOAD_BATCH_SIZE = 5000
CONCURRENT_CONNECTIONS = 5

# Processing Directories
TEMP_DIR = "/tmp/etl_processing/etl_full_xml_test_pipeline"
LOG_DIR = "/var/log/airflow/dags/etl_full_xml_test_pipeline"

# Resource Limits
CPU_CORES = 1.0
MEMORY_MB = 1824
EXECUTION_TIMEOUT_HOURS = 2

# Quality Thresholds
MIN_COMPLETENESS = 0.95
MIN_ACCURACY = 0.98
MAX_DUPLICATES_PCT = 0.05

# Notification Settings
EMAIL_ON_SUCCESS = False
EMAIL_ON_FAILURE = True
NOTIFICATION_EMAILS = ["test_user@company.com"]

# Performance Settings (from AI Recommendations)
# AI рекомендации по производительности не найдены
