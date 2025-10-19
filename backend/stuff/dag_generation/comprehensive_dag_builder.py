"""
DAG Builder - Главный модуль для создания ETL пайплайнов

Этот модуль реализует полный жизненный цикл создания ETL DAG:
1. Анализ источника данных по ссылке
2. Генерация конфигураций Extract, Transform, Load
3. AI рекомендации по оптимизации
4. Создание Airflow DAG кода
5. Метрики и мониторинг

Архитектура: URL → Analysis → Config → Recommendations → DAG → Deploy
"""

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.append("..")

# Import существующих builders
from builders.extract import ExtractConfigBuilder

# Import существующих моделей и builders проекта
from models.extract import ExtractConfig as BasicExtractConfig

from .pipeline_config_models import (
    AIRecommendation,
    CompletePipelineConfig,
    CompletePipelineWithAI,
    ContentType,
    EnhancedExtractConfig,
    EnhancedLoadConfig,
    EnhancedTransformConfig,
    LoadStrategy,
    NotificationConfig,
    OptimizationMetrics,
    PipelineMetadata,
    RecommendationType,
    SourceType,
    TargetStorageType,
)


class ETLPipelineAnalyzer:
    """
    Анализатор ETL пайплайнов для создания полных конфигураций.

    Выполняет:
    - Анализ источников данных
    - Оценку сложности и ресурсов
    - Создание рекомендаций по архитектуре
    """

    def __init__(self):
        """Инициализация анализатора."""
        self.analysis_cache = {}

    async def analyze_source_from_url(self, source_url: str) -> dict[str, Any]:
        """
        Анализ источника данных по URL используя готовые builders.

        Args:
            source_url: URL или путь к источнику данных

        Returns:
            Результаты анализа источника
        """
        print(f"🔍 Анализирую источник: {source_url}")

        try:
            # Пытаемся использовать готовые builders
            extract_config = await self._use_existing_builders(source_url)

            if extract_config:
                print("✅ Используем готовые builders для анализа")
                return await self._analyze_from_extract_config(source_url, extract_config)
            else:
                print("⚠️ Готовые builders не подходят, используем собственную логику")
                return await self._analyze_fallback(source_url)

        except Exception as e:
            print(f"⚠️ Ошибка при использовании builders: {e}")
            return await self._analyze_fallback(source_url)

    async def _use_existing_builders(self, source_url: str) -> BasicExtractConfig | None:
        """Попытка использовать готовые builders для анализа."""
        try:
            # Определяем, можем ли использовать готовые builders
            source = await ExtractConfigBuilder.recognise_source(source_url)

            # Проверяем, поддерживается ли этот тип источника готовыми builders
            if source.source_type == "PostgreSQL":
                print("🐘 Использую PostgreSQL builder")
                return await ExtractConfigBuilder.from_uri(source_url)
            elif source.source_type == "folder":
                # Для folder пока используем собственную логику с XML support
                print("📁 Folder источник - используем расширенную логику")
                return await self._analyze_folder_with_xml_support(source_url, source)
            else:
                return None

        except Exception as e:
            print(f"Ошибка при попытке использовать builders: {e}")
            return None

    async def _analyze_folder_with_xml_support(
        self, source_url: str, source
    ) -> BasicExtractConfig | None:
        """Анализ folder источника с поддержкой XML."""
        from pathlib import Path

        try:
            # Получаем путь к папке
            folder_path = source.connection_string.replace("//", "").replace("file:", "")
            folder_path = Path(folder_path)

            if not folder_path.exists():
                raise ValueError(f"Папка не найдена: {folder_path}")

            # Анализируем содержимое папки
            xml_files = list(folder_path.glob("*.xml"))

            if xml_files:
                print(f"📄 Найдено XML файлов: {len(xml_files)}")

                # Создаем базовый ExtractConfig с XML поддержкой
                from models.extract import Content, ContentType

                content = Content(
                    message_name="xml_files", is_complex_nesting_present=True, metamodel=[]
                )

                # Анализируем первый XML файл для получения структуры
                if xml_files:
                    sample_attributes = await self._analyze_xml_structure(xml_files[0])
                    content.metamodel = sample_attributes

                source.content_type = ContentType.xml

                return BasicExtractConfig(
                    source_metadata=source,
                    content_metadata=content,
                    content_statistics={
                        "total_files": len(xml_files),
                        "total_size_mb": sum(f.stat().st_size for f in xml_files) / (1024 * 1024),
                        "avg_file_size_mb": sum(f.stat().st_size for f in xml_files)
                        / len(xml_files)
                        / (1024 * 1024),
                    },
                )
            else:
                print("⚠️ XML файлы не найдены в папке")
                return None

        except Exception as e:
            print(f"Ошибка анализа folder: {e}")
            return None

    async def _analyze_xml_structure(self, xml_file_path: Path) -> list:
        """Быстрый анализ структуры XML файла."""
        import xml.etree.ElementTree as ET

        from models.extract import Attribute, PostgreSqlDataType

        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()

            attributes = []
            order = 1

            # Простой анализ структуры XML
            for elem in root.iter():
                if elem.text and elem.text.strip():
                    attr = Attribute(
                        order_no=order,
                        column_name=elem.tag,
                        data_type=PostgreSqlDataType.TEXT,
                        is_nullable=True,
                        character_maximum_length=255,
                        numeric_precision=0,
                        numeric_scale=0,
                    )
                    attributes.append(attr)
                    order += 1

                    if order > 20:  # Ограничиваем для демо
                        break

            return attributes

        except Exception as e:
            print(f"Ошибка анализа XML структуры: {e}")
            return []

    async def _analyze_from_extract_config(
        self, source_url: str, extract_config: BasicExtractConfig
    ) -> dict[str, Any]:
        """Анализ на основе готового ExtractConfig."""
        # Преобразуем типы в формат DAG генерации
        source_type = self._convert_source_type(extract_config.source_metadata.source_type)
        content_type = self._convert_content_type(extract_config.content_type)

        # Создаем метрики на основе ExtractConfig
        source_metrics = {
            "estimated_size_mb": extract_config.content_statistics.get("total_size_mb", 50.0)
            if extract_config.content_statistics
            else 50.0,
            "estimated_records": len(extract_config.content_metadata.metamodel) * 1000
            if extract_config.content_metadata and extract_config.content_metadata.metamodel
            else 10000,
            "file_count": extract_config.content_statistics.get("total_files", 1)
            if extract_config.content_statistics
            else 1,
            "avg_record_size_bytes": 1024,
            "complexity_score": min(10.0, len(extract_config.content_metadata.metamodel) * 0.2)
            if extract_config.content_metadata and extract_config.content_metadata.metamodel
            else 5.0,
            "nested_levels": 4
            if extract_config.content_metadata
            and extract_config.content_metadata.is_complex_nesting_present
            else 1,
            "unique_attributes": len(extract_config.content_metadata.metamodel)
            if extract_config.content_metadata and extract_config.content_metadata.metamodel
            else 10,
            "nullable_attributes": sum(
                1 for attr in extract_config.content_metadata.metamodel if attr.is_nullable
            )
            if extract_config.content_metadata and extract_config.content_metadata.metamodel
            else 5,
            "encoding": "utf-8",
            "delimiter": None,
        }

        # Базовая оценка качества данных
        data_quality = {
            "completeness_threshold": 0.95,
            "accuracy_threshold": 0.98,
            "consistency_checks": ["date_format", "data_types", "referential_integrity"],
            "freshness_hours": 24,
            "volume_min_records": 1,
            "volume_max_records": None,
            "schema_drift_detection": True,
            "duplicate_threshold": 0.05,
        }

        return {
            "source_type": source_type,
            "content_type": content_type,
            "source_metrics": source_metrics,
            "data_quality": data_quality,
            "extract_config": extract_config,  # Сохраняем оригинальный конфиг
            "analysis_timestamp": datetime.now(),
        }

    async def _analyze_fallback(self, source_url: str) -> dict[str, Any]:
        """Fallback анализ если builders не работают."""
        # Определение типа источника
        source_type = await self._detect_source_type(source_url)
        content_type = await self._detect_content_type(source_url)

        # Анализ характеристик данных
        source_metrics = await self._analyze_source_metrics(source_url, source_type, content_type)

        # Оценка качества данных
        data_quality = await self._assess_data_quality(source_url, source_type)

        return {
            "source_type": source_type,
            "content_type": content_type,
            "source_metrics": source_metrics,
            "data_quality": data_quality,
            "analysis_timestamp": datetime.now(),
        }

    async def _detect_source_type(self, source_url: str) -> SourceType:
        """Определение типа источника по URL."""
        source_lower = source_url.lower()

        if source_lower.startswith(("http://", "https://")):
            return SourceType.API
        elif source_lower.startswith("s3://"):
            return SourceType.S3
        elif source_lower.startswith("hdfs://"):
            return SourceType.HDFS
        elif source_lower.startswith("kafka://"):
            return SourceType.KAFKA
        elif source_lower.startswith("postgres://") or source_lower.startswith("postgresql://"):
            return SourceType.POSTGRES
        elif source_lower.startswith("clickhouse://"):
            return SourceType.CLICKHOUSE
        elif source_lower.startswith(("ftp://", "sftp://", "ftps://")):
            return SourceType.FTP
        elif source_lower.startswith(("file://", "/", "c:\\", "d:\\")) or Path(source_url).exists():
            return SourceType.FOLDER
        else:
            return SourceType.FOLDER  # По умолчанию

    async def _detect_content_type(self, source_url: str) -> ContentType:
        """Определение формата содержимого."""
        source_lower = source_url.lower()

        # Определение по расширению файла
        if any(ext in source_lower for ext in [".xml", "xml"]):
            return ContentType.XML
        elif any(ext in source_lower for ext in [".json", "json"]):
            return ContentType.JSON
        elif any(ext in source_lower for ext in [".csv", "csv"]):
            return ContentType.CSV
        elif any(ext in source_lower for ext in [".parquet", "parquet"]):
            return ContentType.PARQUET
        elif any(ext in source_lower for ext in [".avro", "avro"]):
            return ContentType.AVRO

        # Определение по типу источника
        source_type = await self._detect_source_type(source_url)
        if source_type in [SourceType.POSTGRES, SourceType.CLICKHOUSE]:
            return ContentType.TABLE
        elif source_type == SourceType.KAFKA:
            return ContentType.JSON  # По умолчанию для Kafka

        return ContentType.XML  # По умолчанию для наших задач

    def _convert_source_type(self, old_source_type) -> SourceType:
        """Конверсия типов источников из models в dag_generation."""
        type_mapping = {
            "folder": SourceType.FOLDER,
            "PostgreSQL": SourceType.POSTGRES,
            "ClickHouse": SourceType.CLICKHOUSE,
            "kafka": SourceType.KAFKA,
            "s3": SourceType.S3,
            "na": SourceType.FOLDER,
        }
        return type_mapping.get(str(old_source_type), SourceType.FOLDER)

    def _convert_content_type(self, old_content_type) -> ContentType:
        """Конверсия типов контента из models в dag_generation."""
        if old_content_type is None:
            return ContentType.XML

        type_mapping = {
            "xml": ContentType.XML,
            "json": ContentType.JSON,
            "csv": ContentType.CSV,
            "parquet": ContentType.PARQUET,
            "avro": ContentType.AVRO,
            "table": ContentType.TABLE,
            "binary": ContentType.BINARY,
            "na": ContentType.XML,
        }
        return type_mapping.get(str(old_content_type), ContentType.XML)

    async def _analyze_source_metrics(
        self, source_url: str, source_type: SourceType, content_type: ContentType
    ) -> dict[str, Any]:
        """Анализ метрик источника данных."""
        # Заглушка - в реальной реализации здесь будет подключение к источнику

        if source_type == SourceType.FOLDER and content_type == ContentType.XML:
            # Анализ XML файлов в папке
            return {
                "estimated_size_mb": 150.5,
                "estimated_records": 25000,
                "file_count": 5,
                "avg_record_size_bytes": 6400,
                "complexity_score": 7.2,
                "nested_levels": 4,
                "unique_attributes": 45,
                "nullable_attributes": 12,
                "encoding": "utf-8",
                "delimiter": None,
            }
        elif source_type == SourceType.POSTGRES:
            # Анализ PostgreSQL таблицы
            return {
                "estimated_size_mb": 1024.0,
                "estimated_records": 1000000,
                "file_count": None,
                "avg_record_size_bytes": 1100,
                "complexity_score": 4.5,
                "nested_levels": 0,
                "unique_attributes": 25,
                "nullable_attributes": 8,
                "encoding": "utf-8",
                "delimiter": None,
            }
        else:
            # Общие оценки
            return {
                "estimated_size_mb": 50.0,
                "estimated_records": 10000,
                "file_count": 1,
                "avg_record_size_bytes": 5000,
                "complexity_score": 5.0,
                "nested_levels": 2,
                "unique_attributes": 20,
                "nullable_attributes": 5,
                "encoding": "utf-8",
                "delimiter": ",",
            }

    async def _assess_data_quality(
        self, source_url: str, source_type: SourceType
    ) -> dict[str, Any]:
        """Оценка качества данных."""
        # Базовые настройки качества данных
        return {
            "completeness_threshold": 0.95,
            "accuracy_threshold": 0.98,
            "consistency_checks": ["date_format", "data_types", "referential_integrity"],
            "freshness_hours": 24,
            "volume_min_records": 1,
            "volume_max_records": None,
            "schema_drift_detection": True,
            "duplicate_threshold": 0.05,
        }


class AIRecommendationEngine:
    """
    AI движок для создания рекомендаций по оптимизации ETL пайплайнов.

    Анализирует:
    - Характеристики данных
    - Целевое хранилище
    - Производительность
    - Стоимость ресурсов
    """

    def __init__(self):
        """Инициализация AI движка."""
        self.recommendation_rules = self._load_recommendation_rules()

    def _load_recommendation_rules(self) -> dict[str, Any]:
        """Загрузка правил для рекомендаций."""
        return {
            "storage_rules": {
                "analytical_workload": TargetStorageType.CLICKHOUSE,
                "transactional_workload": TargetStorageType.POSTGRES,
                "large_scale_analytics": TargetStorageType.CLICKHOUSE,
                "real_time_streaming": TargetStorageType.KAFKA,
            },
            "performance_rules": {
                "batch_size_xml": {"small": 100, "medium": 1000, "large": 5000},
                "parallel_workers": {"low": 1, "medium": 2, "high": 4},
                "memory_allocation": {
                    "xml_parsing": "2GB",
                    "transformation": "4GB",
                    "loading": "1GB",
                },
            },
        }

    async def generate_storage_recommendations(
        self, analysis_results: dict[str, Any]
    ) -> list[AIRecommendation]:
        """Создание рекомендаций по выбору хранилища."""
        recommendations = []

        content_type = analysis_results["content_type"]
        complexity = analysis_results["source_metrics"]["complexity_score"]
        records = analysis_results["source_metrics"]["estimated_records"]

        # Рекомендация для аналитического хранилища
        if content_type in [ContentType.XML, ContentType.JSON] and complexity > 6.0:
            rec = AIRecommendation(
                recommendation_id="storage_analytical_01",
                recommendation_type=RecommendationType.STORAGE_OPTIMIZATION,
                title="Рекомендуется ClickHouse для аналитической нагрузки",
                description="Для сложных XML данных с высокой степенью вложенности ClickHouse обеспечит лучшую производительность аналитических запросов.",
                rationale=f"Сложность данных: {complexity}/10, вложенность: {analysis_results['source_metrics']['nested_levels']} уровней",
                confidence_score=0.85,
                impact_level="high",
                implementation_effort="medium",
                estimated_improvement={"query_performance": 3.5, "compression_ratio": 2.1},
                implementation_steps=[
                    "Создать ClickHouse схему с оптимизированными типами данных",
                    "Настроить партиционирование по дате",
                    "Создать материализованные представления для агрегаций",
                ],
                risks=[
                    "Требует изучения ClickHouse SQL диалекта",
                    "Дополнительные расходы на ClickHouse кластер",
                ],
            )
            recommendations.append(rec)

        # Рекомендация для транзакционной нагрузки
        if records < 100000:
            rec = AIRecommendation(
                recommendation_id="storage_transactional_01",
                recommendation_type=RecommendationType.STORAGE_OPTIMIZATION,
                title="PostgreSQL подходит для небольших объемов данных",
                description="Для объемов данных менее 100K записей PostgreSQL обеспечит отличную производительность с меньшими затратами на инфраструктуру.",
                rationale=f"Объем данных: {records} записей, что позволяет использовать реляционную СУБД",
                confidence_score=0.92,
                impact_level="medium",
                implementation_effort="low",
                estimated_improvement={"cost_reduction": 0.4, "maintenance_simplicity": 0.8},
                implementation_steps=[
                    "Создать оптимизированную PostgreSQL схему",
                    "Настроить индексы для часто используемых полей",
                    "Настроить автоматический VACUUM",
                ],
                risks=["Возможны проблемы с масштабированием при росте данных"],
            )
            recommendations.append(rec)

        return recommendations

    async def generate_performance_recommendations(
        self, analysis_results: dict[str, Any]
    ) -> list[AIRecommendation]:
        """Создание рекомендаций по производительности."""
        recommendations = []

        content_type = analysis_results["content_type"]
        size_mb = analysis_results["source_metrics"]["estimated_size_mb"]
        complexity = analysis_results["source_metrics"]["complexity_score"]

        # Рекомендации для XML обработки
        if content_type == ContentType.XML and complexity > 7.0:
            rec = AIRecommendation(
                recommendation_id="performance_xml_01",
                recommendation_type=RecommendationType.PERFORMANCE_TUNING,
                title="Оптимизация обработки сложных XML данных",
                description="Рекомендуется использовать стриминговый парсинг и увеличить объем памяти для обработки сложных XML структур.",
                rationale=f"Высокая сложность XML ({complexity}/10) требует специальной обработки",
                confidence_score=0.78,
                impact_level="high",
                implementation_effort="medium",
                estimated_improvement={"processing_speed": 2.3, "memory_efficiency": 1.8},
                implementation_steps=[
                    "Включить стриминговый XML парсинг",
                    "Увеличить память до 4GB для transformation задач",
                    "Использовать батчи размером 500 записей",
                    "Включить промежуточное кеширование результатов",
                ],
                risks=["Увеличение потребления памяти", "Необходимость настройки буферизации"],
            )
            recommendations.append(rec)

        # Рекомендации по ресурсам
        if size_mb > 100:
            rec = AIRecommendation(
                recommendation_id="performance_resources_01",
                recommendation_type=RecommendationType.RESOURCE_ALLOCATION,
                title="Увеличение ресурсов для больших объемов данных",
                description="Для обработки больших объемов данных рекомендуется использовать параллельную обработку.",
                rationale=f"Размер данных {size_mb} МБ требует дополнительных ресурсов",
                confidence_score=0.88,
                impact_level="medium",
                implementation_effort="low",
                estimated_improvement={"processing_time": 0.6, "throughput": 2.1},
                implementation_steps=[
                    "Увеличить количество параллельных воркеров до 4",
                    "Выделить 8GB оперативной памяти",
                    "Использовать SSD для временных файлов",
                ],
                risks=["Увеличение стоимости ресурсов"],
            )
            recommendations.append(rec)

        return recommendations

    async def generate_all_recommendations(
        self, analysis_results: dict[str, Any]
    ) -> list[AIRecommendation]:
        """Создание всех рекомендаций для пайплайна."""
        all_recommendations = []

        # Рекомендации по хранилищу
        storage_recs = await self.generate_storage_recommendations(analysis_results)
        all_recommendations.extend(storage_recs)

        # Рекомендации по производительности
        performance_recs = await self.generate_performance_recommendations(analysis_results)
        all_recommendations.extend(performance_recs)

        return all_recommendations


class ComprehensiveDAGBuilder:
    """
    Полноценный построитель DAG для ETL пайплайнов.

    Объединяет:
    - Анализ источников
    - AI рекомендации
    - Создание конфигураций
    - Генерацию DAG кода
    """

    def __init__(self):
        """Инициализация DAG Builder."""
        self.analyzer = ETLPipelineAnalyzer()
        self.ai_engine = AIRecommendationEngine()

    async def build_complete_pipeline_from_url(
        self, source_url: str, pipeline_name: str, owner: str = "data_team", team: str = "analytics"
    ) -> CompletePipelineWithAI:
        """
        Создание полного пайплайна из URL источника.

        Args:
            source_url: URL источника данных
            pipeline_name: Название пайплайна
            owner: Владелец пайплайна
            team: Команда

        Returns:
            Полная конфигурация пайплайна с AI рекомендациями
        """
        print(f"🚀 Создание полного ETL пайплайна: {pipeline_name}")

        # 1. Анализ источника
        print("📊 Шаг 1: Анализ источника данных...")
        analysis_results = await self.analyzer.analyze_source_from_url(source_url)

        # 2. Создание конфигураций ETL
        print("⚙️ Шаг 2: Создание конфигураций Extract, Transform, Load...")
        extract_config = await self._build_extract_config(
            source_url, analysis_results, pipeline_name
        )
        transform_config = await self._build_transform_config(analysis_results, pipeline_name)
        load_config = await self._build_load_config(analysis_results, pipeline_name)

        # 3. Создание метаданных пайплайна
        print("📋 Шаг 3: Создание метаданных пайплайна...")
        metadata = self._build_pipeline_metadata(pipeline_name, owner, team, analysis_results)

        # 4. Создание уведомлений
        notifications = NotificationConfig(
            email_on_failure=True, email_addresses=[f"{owner}@company.com"], slack_webhook=None
        )

        # 5. Сборка основной конфигурации
        pipeline_config = CompletePipelineConfig(
            metadata=metadata,
            pipeline_type="batch_etl",
            extract_config=extract_config,
            transform_config=transform_config,
            load_config=load_config,
            notifications=notifications,
            estimated_runtime_minutes=self._estimate_runtime(analysis_results),
            total_cpu_cores=self._estimate_cpu_requirements(analysis_results),
            total_memory_mb=self._estimate_memory_requirements(analysis_results),
        )

        # 6. Генерация AI рекомендаций
        print("🤖 Шаг 4: Генерация AI рекомендаций...")
        ai_recommendations = await self.ai_engine.generate_all_recommendations(analysis_results)

        # 7. Создание метрик производительности
        baseline_metrics = self._create_baseline_metrics(analysis_results)
        target_metrics = self._create_target_metrics(analysis_results, ai_recommendations)

        # 8. Сборка полной конфигурации
        complete_pipeline = CompletePipelineWithAI(
            pipeline_config=pipeline_config,
            ai_recommendations=ai_recommendations,
            baseline_metrics=baseline_metrics,
            target_metrics=target_metrics,
            config_hash=self._generate_config_hash(pipeline_config),
        )

        print(f"✅ Пайплайн создан успешно! Получено {len(ai_recommendations)} AI рекомендаций")
        return complete_pipeline

    async def _build_extract_config(
        self, source_url: str, analysis: dict, pipeline_name: str
    ) -> EnhancedExtractConfig:
        """Создание расширенной конфигурации извлечения."""
        from .pipeline_config_models import (
            DataQualityProfile,
            ExtractResourceConfig,
            ExtractSchedule,
            IncrementalConfig,
            SourceMetrics,
        )

        # Создание метрик источника
        metrics_data = analysis["source_metrics"]
        source_metrics = SourceMetrics(**metrics_data)

        # Создание профиля качества данных
        quality_data = analysis["data_quality"]
        data_quality = DataQualityProfile(**quality_data)

        # Создание расписания
        schedule = ExtractSchedule(
            frequency="@daily",
            start_date=datetime.now().replace(hour=2, minute=0, second=0, microsecond=0),
            retry_count=3,
            execution_timeout_hours=2,
        )

        # Создание конфигурации ресурсов
        resources = ExtractResourceConfig(
            cpu_cores=1.0 if metrics_data["complexity_score"] < 5 else 2.0,
            memory_mb=512 if metrics_data["estimated_size_mb"] < 50 else 1024,
            parallel_workers=1
            if metrics_data["file_count"] is None
            else min(metrics_data["file_count"], 4),
        )

        # Создание конфигурации инкрементальной загрузки
        incremental_config = IncrementalConfig(
            enabled=False,  # По умолчанию выключено
            lookback_hours=24,
        )

        return EnhancedExtractConfig(
            source_id=f"{pipeline_name}_source",
            source_name=f"Source for {pipeline_name}",
            source_type=analysis["source_type"],
            content_type=analysis["content_type"],
            connection_string=source_url,
            source_metrics=source_metrics,
            data_quality=data_quality,
            batch_size=1000,
            incremental_config=incremental_config,
            schedule=schedule,
            resources=resources,
            schema_validation_rules={},
            business_rules=[],
        )

    async def _build_transform_config(
        self, analysis: dict, pipeline_name: str
    ) -> EnhancedTransformConfig:
        """Создание расширенной конфигурации трансформации."""
        from .pipeline_config_models import (
            DataTypeMapping,
            TransformationRule,
            TransformationType,
            TransformResourceConfig,
            ValidationRule,
        )

        # Создание правил трансформации на основе типа содержимого
        transformation_rules = []
        data_type_mappings = []
        validation_rules = []

        if analysis["content_type"] == ContentType.XML:
            # Правила для XML данных
            transformation_rules.extend(
                [
                    TransformationRule(
                        rule_id="xml_flatten",
                        rule_name="Flatten XML Structure",
                        transformation_type=TransformationType.STANDARDIZATION,
                        source_fields=["xml_content"],
                        target_field="flattened_data",
                        expression="flatten_xml_to_columns(xml_content)",
                        priority=1,
                    ),
                    TransformationRule(
                        rule_id="extract_coordinates",
                        rule_name="Extract Coordinates",
                        transformation_type=TransformationType.ENRICHMENT,
                        source_fields=["spatial_elements"],
                        target_field="coordinate_array",
                        expression="extract_coordinates_from_spatial(spatial_elements)",
                        priority=2,
                    ),
                ]
            )

            # Маппинг типов для XML
            data_type_mappings.extend(
                [
                    DataTypeMapping(
                        source_field="number_pp",
                        source_type="string",
                        target_field="record_id",
                        target_type="varchar(50)",
                    ),
                    DataTypeMapping(
                        source_field="sk_id",
                        source_type="string",
                        target_field="coordinate_system",
                        target_type="varchar(20)",
                    ),
                ]
            )

            # Правила валидации для XML
            validation_rules.extend(
                [
                    ValidationRule(
                        rule_name="Check Record ID",
                        field_name="record_id",
                        validation_type="not_null",
                        parameters={},
                        error_message="Record ID cannot be null",
                        severity="error",
                    )
                ]
            )

        # Конфигурация ресурсов для трансформации
        resources = TransformResourceConfig(
            cpu_cores=2.0,
            memory_mb=2048 if analysis["source_metrics"]["complexity_score"] > 6 else 1024,
            max_parallelism=4,
            spill_to_disk=True,
        )

        return EnhancedTransformConfig(
            transform_id=f"{pipeline_name}_transform",
            transform_name=f"Transform for {pipeline_name}",
            description=f"Data transformation for {analysis['content_type']} content",
            identity_keys=["record_id"],
            aggregate_keys=[],
            transformation_rules=transformation_rules,
            data_type_mappings=data_type_mappings,
            validation_rules=validation_rules,
            resources=resources,
            quality_checks=validation_rules,
            monitoring_metrics=["rows_processed", "transformation_errors", "processing_time"],
        )

    async def _build_load_config(self, analysis: dict, pipeline_name: str) -> EnhancedLoadConfig:
        """Создание расширенной конфигурации загрузки."""
        from .pipeline_config_models import (
            CompressionConfig,
            DataQualityChecks,
            DataRetentionPolicy,
            IndexStrategy,
            LoadResourceConfig,
        )

        # Определение типа целевого хранилища на основе AI рекомендаций
        complexity = analysis["source_metrics"]["complexity_score"]
        records = analysis["source_metrics"]["estimated_records"]

        if complexity > 6.0 and records > 50000:
            target_storage = TargetStorageType.CLICKHOUSE
            connection_string = "clickhouse://localhost:9002/analytics"
        else:
            target_storage = TargetStorageType.POSTGRES
            connection_string = "postgresql://localhost:5432/dwh"

        # Создание стратегий индексации
        indexes = [
            IndexStrategy(
                index_name="idx_record_id",
                index_type="btree",
                columns=["record_id"],
                is_unique=True,
            ),
            IndexStrategy(
                index_name="idx_created_date", index_type="btree", columns=["created_date"]
            ),
        ]

        # Конфигурация сжатия
        compression = CompressionConfig(
            enabled=True,
            algorithm="lz4" if target_storage == TargetStorageType.CLICKHOUSE else "gzip",
        )

        # Конфигурация ресурсов загрузки
        resources = LoadResourceConfig(
            cpu_cores=1.0,
            memory_mb=1024,
            concurrent_connections=5,
            batch_size=10000 if records > 100000 else 5000,
        )

        # Политика хранения данных
        retention_policy = DataRetentionPolicy(
            retention_days=365, archive_after_days=90, compression_enabled=True
        )

        # Проверки качества данных
        quality_checks = DataQualityChecks(
            row_count_validation=True,
            null_checks={"record_id": False},  # record_id не должен быть NULL
            unique_constraints=["record_id"],
        )

        # Маппинг типов данных (заглушка)
        target_schema = []  # Будет заполнено на основе transform_config

        return EnhancedLoadConfig(
            load_id=f"{pipeline_name}_load",
            load_name=f"Load for {pipeline_name}",
            description=f"Data loading to {target_storage.value}",
            target_storage_type=target_storage,
            connection_string=connection_string,
            database_name="dwh" if target_storage == TargetStorageType.POSTGRES else "analytics",
            schema_name="public" if target_storage == TargetStorageType.POSTGRES else "default",
            table_name=f"{pipeline_name}_data",
            load_strategy=LoadStrategy.INCREMENTAL
            if records > 100000
            else LoadStrategy.FULL_REFRESH,
            target_schema=target_schema,
            indexes=indexes,
            compression=compression,
            resources=resources,
            retention_policy=retention_policy,
            quality_checks=quality_checks,
            success_metrics=["rows_loaded", "load_duration", "data_quality_score"],
            notification_channels=["email", "slack"],
        )

    def _build_pipeline_metadata(
        self, pipeline_name: str, owner: str, team: str, analysis: dict
    ) -> PipelineMetadata:
        """Создание метаданных пайплайна."""
        return PipelineMetadata(
            pipeline_id=f"etl_{pipeline_name.lower().replace(' ', '_')}",
            pipeline_name=pipeline_name,
            description=f"ETL pipeline for {analysis['content_type']} data processing",
            owner=owner,
            team=team,
            business_domain="data_processing",
            criticality="medium",
            tags=[analysis["content_type"], analysis["source_type"], "etl", "automated"],
        )

    def _estimate_runtime(self, analysis: dict) -> int:
        """Оценка времени выполнения пайплайна в минутах."""
        size_mb = analysis["source_metrics"]["estimated_size_mb"]
        complexity = analysis["source_metrics"]["complexity_score"]

        # Базовое время + время на размер + время на сложность
        base_time = 5
        size_time = int(size_mb / 10)  # 1 минута на каждые 10MB
        complexity_time = int(complexity * 2)  # 2 минуты на каждый балл сложности

        return base_time + size_time + complexity_time

    def _estimate_cpu_requirements(self, analysis: dict) -> float:
        """Оценка требований к CPU."""
        complexity = analysis["source_metrics"]["complexity_score"]
        size_mb = analysis["source_metrics"]["estimated_size_mb"]

        if complexity > 7.0 or size_mb > 200:
            return 4.0
        elif complexity > 5.0 or size_mb > 100:
            return 2.0
        else:
            return 1.0

    def _estimate_memory_requirements(self, analysis: dict) -> int:
        """Оценка требований к памяти в МБ."""
        size_mb = analysis["source_metrics"]["estimated_size_mb"]
        complexity = analysis["source_metrics"]["complexity_score"]

        # Базовая память + буфер на размер данных + буфер на сложность
        base_memory = 1024
        size_buffer = int(size_mb * 2)  # 2x от размера данных
        complexity_buffer = int(complexity * 200)  # 200MB на балл сложности

        return base_memory + size_buffer + complexity_buffer

    def _create_baseline_metrics(self, analysis: dict) -> OptimizationMetrics:
        """Создание базовых метрик производительности."""
        records = analysis["source_metrics"]["estimated_records"]

        return OptimizationMetrics(
            throughput_records_per_minute=float(records / 60),  # Предполагаем 60 минут на обработку
            latency_minutes=2.0,
            resource_utilization_cpu=0.6,
            resource_utilization_memory=0.7,
            cost_per_execution_usd=0.50,
            data_quality_score=0.85,
            reliability_score=0.90,
        )

    def _create_target_metrics(
        self, analysis: dict, recommendations: list[AIRecommendation]
    ) -> OptimizationMetrics:
        """Создание целевых метрик с учетом AI рекомендаций."""
        baseline = self._create_baseline_metrics(analysis)

        # Применяем улучшения от рекомендаций
        performance_improvement = 1.0
        cost_improvement = 1.0

        for rec in recommendations:
            if rec.recommendation_type == RecommendationType.PERFORMANCE_TUNING:
                if "processing_speed" in rec.estimated_improvement:
                    performance_improvement *= rec.estimated_improvement["processing_speed"]
            elif rec.recommendation_type == RecommendationType.RESOURCE_ALLOCATION:
                if "cost_reduction" in rec.estimated_improvement:
                    cost_improvement *= 1 - rec.estimated_improvement["cost_reduction"]

        return OptimizationMetrics(
            throughput_records_per_minute=baseline.throughput_records_per_minute
            * performance_improvement,
            latency_minutes=baseline.latency_minutes / performance_improvement,
            resource_utilization_cpu=min(baseline.resource_utilization_cpu * 1.2, 0.95),
            resource_utilization_memory=min(baseline.resource_utilization_memory * 1.1, 0.90),
            cost_per_execution_usd=baseline.cost_per_execution_usd * cost_improvement,
            data_quality_score=min(baseline.data_quality_score + 0.05, 0.98),
            reliability_score=min(baseline.reliability_score + 0.03, 0.97),
        )

    def _generate_config_hash(self, config: CompletePipelineConfig) -> str:
        """Генерация хеша конфигурации для отслеживания изменений."""
        config_json = config.json()
        return hashlib.md5(config_json.encode()).hexdigest()

    async def save_pipeline_config(
        self, pipeline: CompletePipelineWithAI, output_dir: str = "generated_pipelines"
    ) -> str:
        """Сохранение конфигурации пайплайна в файл."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        pipeline_id = pipeline.pipeline_config.metadata.pipeline_id
        config_file = output_path / f"{pipeline_id}_config.json"

        # Сохранение в JSON формате
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(pipeline.dict(), f, indent=2, ensure_ascii=False, default=str)

        print(f"💾 Конфигурация пайплайна сохранена: {config_file}")
        return str(config_file)


# Пример использования
async def main():
    """Пример создания полного ETL пайплайна."""
    # Создание DAG Builder
    builder = ComprehensiveDAGBuilder()

    # Создание пайплайна из источника
    pipeline = await builder.build_complete_pipeline_from_url(
        source_url="file://d:/lct-hack-2025/backend/parsers/sample/XML/",
        pipeline_name="Geospatial XML Processing",
        owner="data_engineer",
        team="analytics_team",
    )

    # Сохранение конфигурации
    config_file = await builder.save_pipeline_config(pipeline)

    print("\n🎉 Создан полный ETL пайплайн!")
    print(f"📋 ID: {pipeline.pipeline_config.metadata.pipeline_id}")
    print(
        f"⏱️ Ожидаемое время выполнения: {pipeline.pipeline_config.estimated_runtime_minutes} минут"
    )
    print(f"💻 Требования CPU: {pipeline.pipeline_config.total_cpu_cores} ядер")
    print(f"🧠 Требования RAM: {pipeline.pipeline_config.total_memory_mb} МБ")
    print(f"🤖 AI рекомендации: {len(pipeline.ai_recommendations)}")

    return pipeline


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
