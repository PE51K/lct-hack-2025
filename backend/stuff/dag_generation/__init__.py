"""
DAG Generation System for ETL Pipelines

Полная система автоматической генерации ETL пайплайнов для Apache Airflow.

Основные возможности:
==================

🔍 АНАЛИЗ ДАННЫХ:
- Автоматическое определение типа и формата источника данных
- Анализ структуры и сложности данных
- Оценка метрик качества данных
- Расчет требований к ресурсам

⚙️ КОНФИГУРАЦИЯ ETL:
- Создание полных конфигураций Extract, Transform, Load
- Настройка расписаний и зависимостей
- Определение стратегий обработки данных
- Конфигурация валидации и контроля качества

🤖 AI РЕКОМЕНДАЦИИ:
- Выбор оптимального целевого хранилища
- Рекомендации по производительности
- Оптимизация использования ресурсов
- Стратегии индексации и партиционирования

🏗️ ГЕНЕРАЦИЯ КОДА:
- Создание готовых Airflow DAG файлов
- Генерация функций задач с обработкой ошибок
- Автоматическая интеграция с существующими парсерами
- Конфигурационные файлы и документация

📋 МОНИТОРИНГ И РАЗВЕРТЫВАНИЕ:
- Подробная документация по развертыванию
- Инструкции по настройке подключений
- Метрики производительности и SLA
- Готовые скрипты для тестирования

Архитектура системы:
==================

URL/Path → Analyzer → Config Builder → AI Engine → DAG Generator → Airflow Deploy

Компоненты:
----------
- ETLPipelineAnalyzer: Анализ источников данных
- ComprehensiveDAGBuilder: Создание конфигураций пайплайнов
- AIRecommendationEngine: Генерация AI рекомендаций
- EnhancedAirflowDAGGenerator: Создание Airflow кода
- ETLDAGGenerationSystem: Главный интерфейс системы

Пример использования:
===================

from dag_generation import ETLDAGGenerationSystem

# Создание системы
dag_system = ETLDAGGenerationSystem()

# Генерация пайплайна
result = await dag_system.create_complete_etl_pipeline(
    source_url="file://path/to/xml/files/",
    pipeline_name="XML Processing Pipeline",
    owner="data_engineer",
    team="analytics"
)

# Результат содержит:
# - pipeline_config: Полная конфигурация
# - generated_files: Пути к Airflow файлам
# - ai_recommendations: AI рекомендации
# - report_file: Подробный отчет

Поддерживаемые источники:
========================
- Папки с файлами (XML, JSON, CSV)
- PostgreSQL базы данных
- ClickHouse хранилища
- S3 объектные хранилища
- Kafka топики
- HTTP API эндпоинты
- FTP/SFTP серверы

Целевые хранилища:
=================
- PostgreSQL (для транзакционных данных)
- ClickHouse (для аналитических данных)
- HDFS (для больших данных)
- S3 (для архивирования)
- Elasticsearch (для поиска)
- Redis (для кеширования)

AI оптимизации:
==============
- Автоматический выбор хранилища по характеристикам данных
- Оптимизация размеров батчей и параллелизма
- Рекомендации по индексации и партиционированию
- Настройка расписаний на основе SLA
- Оптимизация использования ресурсов CPU/RAM

Создано для проекта LCT-hack-2025
Команда: AI Data Assistant
"""

from .comprehensive_dag_builder import (
    AIRecommendationEngine,
    ComprehensiveDAGBuilder,
    ETLPipelineAnalyzer,
)
from .enhanced_airflow_generator import EnhancedAirflowDAGGenerator
from .etl_dag_system import ETLDAGGenerationSystem
from .pipeline_config_models import (
    # AI и метрики
    AIRecommendation,
    CompletePipelineConfig,
    # Основные конфигурации
    CompletePipelineWithAI,
    ContentType,
    DataQualityProfile,
    EnhancedExtractConfig,
    EnhancedLoadConfig,
    EnhancedTransformConfig,
    LoadStrategy,
    NotificationConfig,
    OptimizationMetrics,
    # Вспомогательные модели
    PipelineMetadata,
    PipelineType,
    RecommendationType,
    SourceMetrics,
    # Enums
    SourceType,
    TargetStorageType,
    TransformationType,
)

# Версия системы
__version__ = "2.0.0"

# Основные экспорты
__all__ = [
    # Главный интерфейс
    "ETLDAGGenerationSystem",
    # Основные компоненты
    "ComprehensiveDAGBuilder",
    "ETLPipelineAnalyzer",
    "AIRecommendationEngine",
    "EnhancedAirflowDAGGenerator",
    # Конфигурационные модели
    "CompletePipelineWithAI",
    "CompletePipelineConfig",
    "EnhancedExtractConfig",
    "EnhancedTransformConfig",
    "EnhancedLoadConfig",
    # Перечисления
    "SourceType",
    "ContentType",
    "TargetStorageType",
    "LoadStrategy",
    "TransformationType",
    "PipelineType",
    "RecommendationType",
    # AI и оптимизация
    "AIRecommendation",
    "OptimizationMetrics",
    # Метаданные и настройки
    "PipelineMetadata",
    "NotificationConfig",
    "DataQualityProfile",
    "SourceMetrics",
    # Версия
    "__version__",
]


# Вспомогательные функции для быстрого старта
async def quick_xml_pipeline(xml_path: str, pipeline_name: str) -> dict:
    """
    Быстрое создание пайплайна для XML файлов.

    Args:
        xml_path: Путь к XML файлам
        pipeline_name: Название пайплайна

    Returns:
        Результат создания пайплайна
    """
    system = ETLDAGGenerationSystem()
    return await system.create_complete_etl_pipeline(
        source_url=f"file://{xml_path}",
        pipeline_name=pipeline_name,
        owner="xml_processor",
        team="data_processing",
    )


async def quick_postgres_pipeline(connection_string: str, pipeline_name: str) -> dict:
    """
    Быстрое создание пайплайна для PostgreSQL.

    Args:
        connection_string: Строка подключения PostgreSQL
        pipeline_name: Название пайплайна

    Returns:
        Результат создания пайплайна
    """
    system = ETLDAGGenerationSystem()
    return await system.create_complete_etl_pipeline(
        source_url=connection_string,
        pipeline_name=pipeline_name,
        owner="postgres_processor",
        team="database_team",
    )


def print_system_info():
    """Вывод информации о системе."""
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                    ETL DAG GENERATION SYSTEM                     ║
║                         Version {__version__}                           ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║  
║  🚀 Автоматическая генерация ETL пайплайнов для Apache Airflow   ║
║                                                                  ║
║  Возможности:                                                    ║
║  • 🔍 Анализ источников данных                                   ║
║  • ⚙️  Создание конфигураций Extract/Transform/Load              ║
║  • 🤖 AI рекомендации по оптимизации                            ║
║  • 🏗️  Генерация готового Airflow кода                         ║
║  • 📋 Документация и развертывание                               ║
║                                                                  ║
║  Поддерживаемые форматы: XML, JSON, CSV, Parquet                ║
║  Источники: Файлы, PostgreSQL, ClickHouse, S3, Kafka           ║
║  Целевые системы: PostgreSQL, ClickHouse, HDFS, S3             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)


# Константы системы
DEFAULT_OUTPUT_DIR = "generated_etl_pipelines"
SUPPORTED_SOURCE_TYPES = [e.value for e in SourceType]
SUPPORTED_CONTENT_TYPES = [e.value for e in ContentType]
SUPPORTED_TARGET_STORAGE = [e.value for e in TargetStorageType]

# Настройки по умолчанию
DEFAULT_BATCH_SIZE = 1000
DEFAULT_PARALLEL_WORKERS = 2
DEFAULT_CPU_CORES = 2.0
DEFAULT_MEMORY_MB = 2048
DEFAULT_EXECUTION_TIMEOUT_HOURS = 2

# Пороги качества данных по умолчанию
DEFAULT_COMPLETENESS_THRESHOLD = 0.95
DEFAULT_ACCURACY_THRESHOLD = 0.98
DEFAULT_DUPLICATE_THRESHOLD = 0.05

# AI настройки
AI_CONFIDENCE_THRESHOLD = 0.7  # Минимальная уверенность для применения рекомендаций
AI_MAX_RECOMMENDATIONS = 10  # Максимальное количество рекомендаций

if __name__ == "__main__":
    print_system_info()
