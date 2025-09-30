"""
Configuration file for Demo Geospatial XML Processing

Содержит все константы и настройки для DAG.
"""

# DAG Configuration
DAG_ID = "etl_demo_geospatial_xml_processing"
DAG_NAME = "Demo Geospatial XML Processing"
DAG_OWNER = "demo_user"

# Source Configuration
SOURCE_PATH = "file://d:/lct-hack-2025/backend/parsers/sample/XML/"
SOURCE_TYPE = "folder"
CONTENT_TYPE = "xml"

# Processing Configuration
BATCH_SIZE = 1000
PARALLEL_WORKERS = 4
MAX_DATA_SIZE_BYTES = 1073741824

# Target Configuration
TARGET_STORAGE_TYPE = "postgres"
TARGET_CONNECTION = "postgresql://localhost:5432/dwh"
TARGET_DATABASE = "dwh"
TARGET_SCHEMA = "public"
TARGET_TABLE = "Demo Geospatial XML Processing_data"

# Load Configuration
LOAD_STRATEGY = "full_refresh"
LOAD_BATCH_SIZE = 5000
CONCURRENT_CONNECTIONS = 5

# Processing Directories
TEMP_DIR = "/tmp/etl_processing/etl_demo_geospatial_xml_processing"
LOG_DIR = "/var/log/airflow/dags/etl_demo_geospatial_xml_processing"

# Resource Limits
CPU_CORES = 4.0
MEMORY_MB = 2765
EXECUTION_TIMEOUT_HOURS = 2

# Quality Thresholds
MIN_COMPLETENESS = 0.95
MIN_ACCURACY = 0.98
MAX_DUPLICATES_PCT = 0.05

# Notification Settings
EMAIL_ON_SUCCESS = False
EMAIL_ON_FAILURE = True
NOTIFICATION_EMAILS = ["demo_user@company.com"]

# Performance Settings (from AI Recommendations)
# AI Рекомендация: Оптимизация обработки сложных XML данных
ENABLE_STREAMING_PARSING = True  # Улучшение: 2.3x
ENABLE_MEMORY_OPTIMIZATION = True  # Улучшение: 1.8x
# AI Рекомендация: Увеличение ресурсов для больших объемов данных
ENABLE_PARALLEL_PROCESSING = True
