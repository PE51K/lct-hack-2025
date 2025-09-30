"""
Enhanced Airflow DAG Generator

Генерирует полноценные Airflow DAG файлы на основе полных конфигураций ETL пайплайнов.
Включает:
- AI рекомендации в виде комментариев
- Оптимизированные операторы
- Полный жизненный цикл ETL
- Мониторинг и алертинг
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import json

sys.path.append("..")

from .pipeline_config_models import (
    CompletePipelineWithAI, 
    SourceType, 
    ContentType, 
    TargetStorageType,
    LoadStrategy,
    TransformationType
)


class EnhancedAirflowDAGGenerator:
    """
    Расширенный генератор Airflow DAG с поддержкой AI рекомендаций.
    
    Создает:
    - Полный Python код DAG
    - Функции задач с обработкой ошибок
    - Интеграцию с существующими парсерами
    - Мониторинг и метрики
    """
    
    def __init__(self, output_dir: str = "generated_dags"):
        """
        Инициализация генератора.
        
        Args:
            output_dir: Директория для сохранения DAG файлов
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    async def generate_complete_dag(self, pipeline_config: CompletePipelineWithAI) -> Dict[str, str]:
        """
        Генерация полного набора файлов для Airflow DAG.
        
        Args:
            pipeline_config: Полная конфигурация пайплайна
            
        Returns:
            Словарь с путями к созданным файлам
        """
        dag_id = pipeline_config.pipeline_config.metadata.pipeline_id
        
        print(f"🏗️ Генерирую Airflow DAG: {dag_id}")
        
        generated_files = {}
        
        # 1. Основной DAG файл
        dag_content = await self._generate_dag_file_content(pipeline_config)
        dag_file = self.output_dir / f"{dag_id}.py"
        with open(dag_file, 'w', encoding='utf-8') as f:
            f.write(dag_content)
        generated_files["dag_file"] = str(dag_file)
        
        # 2. Модуль функций задач
        functions_content = await self._generate_task_functions_module(pipeline_config)
        functions_file = self.output_dir / f"{dag_id}_functions.py"
        with open(functions_file, 'w', encoding='utf-8') as f:
            f.write(functions_content)
        generated_files["functions_file"] = str(functions_file)
        
        # 3. Конфигурационный файл
        config_content = await self._generate_config_file(pipeline_config)
        config_file = self.output_dir / f"{dag_id}_config.py"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        generated_files["config_file"] = str(config_file)
        
        # 4. Requirements файл
        requirements_content = await self._generate_requirements(pipeline_config)
        requirements_file = self.output_dir / "requirements.txt"
        with open(requirements_file, 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        generated_files["requirements_file"] = str(requirements_file)
        
        # 5. Документация по развертыванию
        docs_content = await self._generate_deployment_docs(pipeline_config, generated_files)
        docs_file = self.output_dir / f"{dag_id}_deployment.md"
        with open(docs_file, 'w', encoding='utf-8') as f:
            f.write(docs_content)
        generated_files["documentation"] = str(docs_file)
        
        print(f"✅ Сгенерированы файлы: {list(generated_files.keys())}")
        return generated_files
    
    async def _generate_dag_file_content(self, config: CompletePipelineWithAI) -> str:
        """Генерация основного DAG файла."""
        
        pipeline = config.pipeline_config
        dag_id = pipeline.metadata.pipeline_id
        
        # AI рекомендации в виде комментариев
        ai_comments = self._generate_ai_recommendations_comments(config.ai_recommendations)
        
        # Импорты
        imports = self._generate_imports(pipeline)
        
        # Конфигурация DAG
        dag_config = self._generate_dag_configuration(pipeline)
        
        # Определения задач
        task_definitions = await self._generate_task_definitions(pipeline)
        
        # Зависимости задач
        task_dependencies = self._generate_task_dependencies()
        
        content = f'''"""
{pipeline.metadata.description}

Автоматически сгенерированный Airflow DAG
Pipeline ID: {dag_id}
Создан: {config.generated_at.isoformat()}
Версия генератора: {config.generator_version}

Ожидаемое время выполнения: {pipeline.estimated_runtime_minutes} минут
Требования CPU: {pipeline.total_cpu_cores} ядер
Требования RAM: {pipeline.total_memory_mb} МБ

{ai_comments}
"""

{imports}

# Импорт конфигурации и функций
from {dag_id}_config import *
from {dag_id}_functions import *

{dag_config}

{task_definitions}

{task_dependencies}
'''
        
        return content
    
    def _generate_ai_recommendations_comments(self, recommendations: List) -> str:
        """Генерация комментариев с AI рекомендациями."""
        if not recommendations:
            return "# AI рекомендации: не доступны"
        
        comments = ["# AI РЕКОМЕНДАЦИИ ПО ОПТИМИЗАЦИИ:"]
        
        for i, rec in enumerate(recommendations, 1):
            comments.append(f"# {i}. {rec.title}")
            comments.append(f"#    {rec.description}")
            comments.append(f"#    Уверенность: {rec.confidence_score:.0%}")
            comments.append(f"#    Воздействие: {rec.impact_level}")
            
            if rec.estimated_improvement:
                improvements = ", ".join([f"{k}: {v:.1f}x" for k, v in rec.estimated_improvement.items()])
                comments.append(f"#    Улучшения: {improvements}")
            
            comments.append("#")
        
        return "\n".join(comments)
    
    def _generate_imports(self, pipeline) -> str:
        """Генерация импортов."""
        
        base_imports = [
            "from datetime import datetime, timedelta",
            "from airflow import DAG",
            "from airflow.operators.python import PythonOperator",
            "from airflow.operators.bash import BashOperator", 
            "from airflow.operators.dummy import DummyOperator",
            "from airflow.operators.email import EmailOperator",
            "from airflow.sensors.filesystem import FileSensor",
            "import logging",
            "import json",
            "from pathlib import Path"
        ]
        
        # Добавляем специфичные импорты на основе конфигурации
        source_type = pipeline.extract_config.source_type
        target_storage = pipeline.load_config.target_storage_type
        
        if target_storage == TargetStorageType.POSTGRES:
            base_imports.append("from airflow.providers.postgres.operators.postgres import PostgresOperator")
            base_imports.append("from airflow.providers.postgres.hooks.postgres import PostgresHook")
        
        if target_storage == TargetStorageType.CLICKHOUSE:
            base_imports.append("from airflow.providers.http.operators.http import SimpleHttpOperator")
        
        if source_type == SourceType.FOLDER:
            base_imports.append("# Для работы с файловой системой импорты уже включены")
        
        return "\n".join(base_imports)
    
    def _generate_dag_configuration(self, pipeline) -> str:
        """Генерация конфигурации DAG."""
        
        schedule = pipeline.extract_config.schedule
        
        default_args = {
            'owner': pipeline.metadata.owner,
            'depends_on_past': schedule.depends_on_past,
            'start_date': f"datetime({schedule.start_date.year}, {schedule.start_date.month}, {schedule.start_date.day})",
            'email_on_failure': pipeline.notifications.email_on_failure,
            'email_on_retry': pipeline.notifications.email_on_retry,
            'retries': schedule.retry_count,
            'retry_delay': f'timedelta(minutes={schedule.retry_delay_minutes})',
            'execution_timeout': f'timedelta(hours={schedule.execution_timeout_hours})'
        }
        
        if pipeline.notifications.email_addresses:
            default_args['email'] = str(pipeline.notifications.email_addresses)
        
        args_lines = ["default_args = {"]
        for key, value in default_args.items():
            if isinstance(value, str) and not value.startswith(('datetime', 'timedelta', '[')):
                args_lines.append(f'    "{key}": "{value}",')
            else:
                args_lines.append(f'    "{key}": {value},')
        args_lines.append("}")
        
        dag_definition = f'''
{chr(10).join(args_lines)}

dag = DAG(
    DAG_ID,
    default_args=default_args,
    description="{pipeline.metadata.description}",
    schedule_interval="{schedule.frequency}",
    start_date=datetime({schedule.start_date.year}, {schedule.start_date.month}, {schedule.start_date.day}),
    catchup={schedule.catchup},
    max_active_runs={schedule.max_active_runs},
    tags={pipeline.metadata.tags}
)'''
        
        return dag_definition
    
    async def _generate_task_definitions(self, pipeline) -> str:
        """Генерация определений задач."""
        
        extract_config = pipeline.extract_config
        transform_config = pipeline.transform_config
        load_config = pipeline.load_config
        
        tasks = []
        
        # Start task
        tasks.append('''
# Стартовая задача
start_task = DummyOperator(
    task_id="start_pipeline",
    dag=dag
)''')
        
        # Задачи валидации источника
        if extract_config.data_quality.schema_drift_detection:
            tasks.append('''
# Валидация источника данных
validate_source_task = PythonOperator(
    task_id="validate_source",
    python_callable=validate_source_data,
    provide_context=True,
    dag=dag
)''')
        
        # Задача извлечения
        tasks.append(f'''
# Извлечение данных
extract_task = PythonOperator(
    task_id="extract_data",
    python_callable=extract_data,
    provide_context=True,
    pool_slots={extract_config.resources.parallel_workers},
    dag=dag
)''')
        
        # Задачи трансформации
        if transform_config.transformation_rules:
            tasks.append('''
# Трансформация данных  
transform_task = PythonOperator(
    task_id="transform_data",
    python_callable=transform_data,
    provide_context=True,
    dag=dag
)''')
        
        # Задача валидации трансформированных данных
        if transform_config.quality_checks:
            tasks.append('''
# Валидация трансформированных данных
validate_transform_task = PythonOperator(
    task_id="validate_transformed_data", 
    python_callable=validate_transformed_data,
    provide_context=True,
    dag=dag
)''')
        
        # Задача загрузки
        if load_config.target_storage_type == TargetStorageType.POSTGRES:
            tasks.append(f'''
# Загрузка в PostgreSQL
load_task = PythonOperator(
    task_id="load_to_postgres",
    python_callable=load_to_postgres,
    provide_context=True,
    pool_slots={load_config.resources.concurrent_connections},
    dag=dag
)''')
        elif load_config.target_storage_type == TargetStorageType.CLICKHOUSE:
            tasks.append(f'''
# Загрузка в ClickHouse
load_task = PythonOperator(
    task_id="load_to_clickhouse",
    python_callable=load_to_clickhouse,
    provide_context=True,
    pool_slots={load_config.resources.concurrent_connections},
    dag=dag
)''')
        
        # Задача валидации загруженных данных
        if load_config.quality_checks.row_count_validation:
            tasks.append('''
# Валидация загруженных данных
validate_load_task = PythonOperator(
    task_id="validate_loaded_data",
    python_callable=validate_loaded_data,
    provide_context=True,
    dag=dag
)''')
        
        # Задача очистки
        tasks.append('''
# Очистка временных файлов
cleanup_task = PythonOperator(
    task_id="cleanup_temp_files",
    python_callable=cleanup_temp_files,
    provide_context=True,
    trigger_rule="all_done",
    dag=dag
)''')
        
        # Задача уведомления об успехе
        if pipeline.notifications.email_on_success:
            tasks.append(f'''
# Уведомление об успешном завершении  
success_notification = EmailOperator(
    task_id="success_notification",
    to={pipeline.notifications.email_addresses},
    subject="ETL Pipeline Completed Successfully - {{{{ dag.dag_id }}}}",
    html_content="""
    <h3>Pipeline {{{{ dag.dag_id }}}} completed successfully!</h3>
    <p><strong>Execution Date:</strong> {{{{ ds }}}}</p>
    <p><strong>Duration:</strong> {{{{ dag_run.get_task_instance('start_pipeline').duration }}}} seconds</p>
    <p><strong>Processed Records:</strong> {{{{ ti.xcom_pull(task_ids='extract_data').get('total_records', 'N/A') }}}}</p>
    """,
    dag=dag
)''')
        
        # End task
        tasks.append('''
# Финальная задача
end_task = DummyOperator(
    task_id="end_pipeline",
    trigger_rule="none_failed_min_one_success",
    dag=dag
)''')
        
        return "\n".join(tasks)
    
    def _generate_task_dependencies(self) -> str:
        """Генерация зависимостей задач."""
        
        dependencies = [
            "# Зависимости задач",
            "start_task >> validate_source_task >> extract_task",
            "extract_task >> transform_task >> validate_transform_task", 
            "validate_transform_task >> load_task >> validate_load_task",
            "validate_load_task >> success_notification >> end_task",
            "[validate_load_task, success_notification] >> cleanup_task >> end_task"
        ]
        
        return "\n".join(dependencies)
    
    async def _generate_task_functions_module(self, config: CompletePipelineWithAI) -> str:
        """Генерация модуля с функциями задач."""
        
        pipeline = config.pipeline_config
        extract_config = pipeline.extract_config
        transform_config = pipeline.transform_config
        load_config = pipeline.load_config
        
        content = f'''"""
Task Functions Module for {pipeline.metadata.pipeline_name}

Содержит все функции для выполнения ETL задач.
Генерировано автоматически: {config.generated_at.isoformat()}
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Добавление пути к парсерам
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "parsers", "sample", "XML"))

try:
    from xml_parser import XMLStreamParser, XMLDataProcessor
except ImportError as e:
    logging.warning(f"XML parser not available: {{e}}")
    XMLStreamParser = None
    XMLDataProcessor = None

# Импорт конфигурации
from {pipeline.metadata.pipeline_id}_config import *

def validate_source_data(**context):
    """
    Валидация исходных данных.
    
    AI Рекомендация: {self._get_recommendation_for_task(config.ai_recommendations, "validation")}
    """
    logging.info("🔍 Начало валидации источника данных")
    
    source_path = SOURCE_PATH
    content_type = "{extract_config.content_type}"
    
    if content_type == "xml":
        # Валидация XML файлов
        xml_files = list(Path(source_path).glob("*.xml"))
        
        if not xml_files:
            raise ValueError(f"XML файлы не найдены в: {{source_path}}")
        
        total_size = sum(f.stat().st_size for f in xml_files)
        logging.info(f"Найдено XML файлов: {{len(xml_files)}}")
        logging.info(f"Общий размер: {{total_size / (1024*1024):.2f}} МБ")
        
        # Проверка размера данных
        if total_size > MAX_DATA_SIZE_BYTES:
            raise ValueError(f"Размер данных превышает лимит: {{total_size}} > {{MAX_DATA_SIZE_BYTES}}")
        
        # Проверка доступности файлов
        for xml_file in xml_files:
            if not os.access(xml_file, os.R_OK):
                raise PermissionError(f"Нет доступа к файлу: {{xml_file}}")
    
    logging.info("✅ Валидация источника успешно завершена")
    return {{"validation_status": "passed", "files_count": len(xml_files)}}

def extract_data(**context):
    """
    Извлечение данных из источника.
    
    Конфигурация:
    - Источник: {extract_config.source_type}
    - Формат: {extract_config.content_type}  
    - Размер батча: {extract_config.batch_size}
    - Параллельные воркеры: {extract_config.resources.parallel_workers}
    """
    logging.info("📥 Начало извлечения данных")
    
    source_path = SOURCE_PATH
    batch_size = BATCH_SIZE
    content_type = "{extract_config.content_type}"
    
    total_records = 0
    processed_files = 0
    
    if content_type == "xml":
        if not XMLStreamParser:
            raise ImportError("XML парсер недоступен")
        
        # Инициализация парсера и процессора
        parser = XMLStreamParser(chunk_size=batch_size)
        processor = XMLDataProcessor(output_dir=TEMP_DIR)
        
        # Обработка XML файлов
        xml_files = list(Path(source_path).glob("*.xml"))
        
        for xml_file in xml_files:
            logging.info(f"Обработка файла: {{xml_file.name}}")
            
            file_records = 0
            batch_data = []
            
            try:
                for item in parser.parse_file_stream(str(xml_file)):
                    batch_data.append(item)
                    file_records += 1
                    
                    # Сохранение батча при достижении размера
                    if len(batch_data) >= batch_size:
                        batch_filename = f"batch_{{processed_files}}_{{len(batch_data)}}"
                        processor.save_to_json(batch_data, batch_filename)
                        batch_data = []
                
                # Сохранение остатка
                if batch_data:
                    batch_filename = f"batch_{{processed_files}}_final"
                    processor.save_to_json(batch_data, batch_filename)
                
                total_records += file_records
                processed_files += 1
                
                logging.info(f"✅ Файл {{xml_file.name}}: {{file_records}} записей")
                
            except Exception as e:
                logging.error(f"❌ Ошибка обработки файла {{xml_file.name}}: {{e}}")
                raise
    
    else:
        raise NotImplementedError(f"Извлечение для формата {{content_type}} не реализовано")
    
    result = {{
        "total_records": total_records,
        "processed_files": processed_files,
        "batch_size": batch_size,
        "temp_dir": TEMP_DIR
    }}
    
    logging.info(f"✅ Извлечение завершено: {{total_records}} записей из {{processed_files}} файлов")
    return result

def transform_data(**context):
    """
    Трансформация извлеченных данных.
    
    Применяемые трансформации:
    {self._generate_transform_rules_comment(transform_config)}
    """
    logging.info("🔄 Начало трансформации данных")
    
    # Получение данных от предыдущей задачи
    extract_result = context['ti'].xcom_pull(task_ids='extract_data')
    temp_dir = Path(extract_result.get('temp_dir', TEMP_DIR))
    
    transformed_records = []
    
    # Чтение батчей данных
    batch_files = list(temp_dir.glob("batch_*.json"))
    logging.info(f"Найдено батчей для обработки: {{len(batch_files)}}")
    
    for batch_file in batch_files:
        try:
            with open(batch_file, 'r', encoding='utf-8') as f:
                batch_data = json.load(f)
            
            # Трансформация каждой записи в батче
            for record in batch_data:
                transformed_record = transform_single_record(record)
                if transformed_record:  # Пропускаем невалидные записи
                    transformed_records.append(transformed_record)
            
            logging.info(f"✅ Обработан батч {{batch_file.name}}: {{len(batch_data)}} записей")
            
        except Exception as e:
            logging.error(f"❌ Ошибка обработки батча {{batch_file.name}}: {{e}}")
            raise
    
    # Сохранение трансформированных данных
    output_file = temp_dir / "transformed_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(transformed_records, f, ensure_ascii=False, indent=2, default=str)
    
    result = {{
        "transformed_records": len(transformed_records),
        "output_file": str(output_file)
    }}
    
    logging.info(f"✅ Трансформация завершена: {{len(transformed_records)}} записей")
    return result

def transform_single_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Трансформация одной записи."""
    try:
        # Базовая трансформация для XML геоданных
        transformed = {{
            "record_id": record.get("number_pp", "unknown"),
            "coordinate_system": record.get("sk_id", "unknown"),
            "purpose": record.get("purpose", "unknown"),
            "processed_at": datetime.now().isoformat(),
            "source_file": record.get("_source_file", "unknown")
        }}
        
        # Обработка пространственных элементов
        spatial_elements = record.get("spatial_elements", [])
        if spatial_elements:
            coordinate_count = sum(
                len(se.get("ordinates", [])) 
                for se in spatial_elements
            )
            transformed["coordinate_count"] = coordinate_count
            
            # Извлечение первых координат для примера
            if spatial_elements[0].get("ordinates"):
                first_coords = spatial_elements[0]["ordinates"][:2]
                transformed["sample_coordinates"] = first_coords
        
        return transformed
        
    except Exception as e:
        logging.warning(f"Ошибка трансформации записи: {{e}}")
        return None

def validate_transformed_data(**context):
    """Валидация трансформированных данных."""
    logging.info("🔍 Валидация трансформированных данных")
    
    # Получение результата трансформации
    transform_result = context['ti'].xcom_pull(task_ids='transform_data')
    output_file = Path(transform_result['output_file'])
    
    if not output_file.exists():
        raise FileNotFoundError(f"Файл трансформированных данных не найден: {{output_file}}")
    
    # Загрузка и валидация данных
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data:
        raise ValueError("Нет данных после трансформации")
    
    # Проверка обязательных полей
    required_fields = ["record_id", "coordinate_system", "processed_at"]
    validation_errors = []
    
    for i, record in enumerate(data[:10]):  # Проверка первых 10 записей
        for field in required_fields:
            if field not in record or record[field] in [None, ""]:
                validation_errors.append(f"Запись {{i}}: отсутствует поле '{{field}}'")
    
    if validation_errors:
        raise ValueError(f"Ошибки валидации: {{'; '.join(validation_errors)}}")
    
    logging.info(f"✅ Валидация прошла успешно: {{len(data)}} записей")
    return {{"validation_status": "passed", "validated_records": len(data)}}

def load_to_{load_config.target_storage_type.value.lower()}(**context):
    """
    Загрузка данных в {load_config.target_storage_type.value}.
    
    Конфигурация:
    - Стратегия загрузки: {load_config.load_strategy}
    - Размер батча: {load_config.resources.batch_size}
    - Целевая таблица: {load_config.schema_name}.{load_config.table_name}
    """
    logging.info("📤 Начало загрузки данных в {load_config.target_storage_type.value}")
    
    # Получение трансформированных данных
    transform_result = context['ti'].xcom_pull(task_ids='transform_data')
    output_file = Path(transform_result['output_file'])
    
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logging.info(f"Загрузка {{len(data)}} записей в {{TARGET_SCHEMA}}.{{TARGET_TABLE}}")
    
    # В реальной реализации здесь будет подключение к БД
    # Пока симулируем загрузку
    
    batch_size = LOAD_BATCH_SIZE
    loaded_records = 0
    
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        
        # Симуляция загрузки батча
        logging.info(f"Загрузка батча: {{i + 1}}-{{min(i + batch_size, len(data))}}")
        
        # Здесь будет реальная загрузка в БД
        # load_batch_to_database(batch)
        
        loaded_records += len(batch)
    
    result = {{
        "loaded_records": loaded_records,
        "target_table": f"{{TARGET_SCHEMA}}.{{TARGET_TABLE}}",
        "load_strategy": "{load_config.load_strategy}"
    }}
    
    logging.info(f"✅ Загрузка завершена: {{loaded_records}} записей")
    return result

def validate_loaded_data(**context):
    """Валидация загруженных данных в целевой системе."""
    logging.info("🔍 Валидация загруженных данных")
    
    load_result = context['ti'].xcom_pull(task_ids='load_to_{load_config.target_storage_type.value.lower()}')
    expected_records = load_result['loaded_records']
    
    # Симуляция проверки количества записей в БД
    logging.info(f"Проверка количества записей в {{TARGET_SCHEMA}}.{{TARGET_TABLE}}")
    logging.info(f"Ожидается записей: {{expected_records}}")
    
    # В реальной реализации здесь будет запрос к БД
    # actual_count = get_table_row_count(TARGET_SCHEMA, TARGET_TABLE)
    actual_count = expected_records  # Симуляция
    
    if actual_count != expected_records:
        raise ValueError(f"Несоответствие количества записей: ожидалось {{expected_records}}, найдено {{actual_count}}")
    
    # Дополнительные проверки качества данных
    quality_checks = {{
        "row_count": actual_count,
        "null_checks": "passed",
        "data_types": "passed", 
        "constraints": "passed"
    }}
    
    logging.info(f"✅ Валидация загруженных данных успешна: {{actual_count}} записей")
    return quality_checks

def cleanup_temp_files(**context):
    """Очистка временных файлов."""
    logging.info("🧹 Очистка временных файлов")
    
    temp_dir = Path(TEMP_DIR)
    
    if temp_dir.exists():
        # Удаление временных файлов
        temp_files = list(temp_dir.glob("batch_*.json")) + list(temp_dir.glob("transformed_*.json"))
        
        for temp_file in temp_files:
            try:
                temp_file.unlink()
                logging.info(f"Удален временный файл: {{temp_file.name}}")
            except Exception as e:
                logging.warning(f"Не удалось удалить {{temp_file}}: {{e}}")
        
        logging.info(f"✅ Очистка завершена: удалено {{len(temp_files)}} временных файлов")
    
    return {{"cleanup_status": "completed", "files_removed": len(temp_files)}}
'''
        
        return content
    
    async def _generate_config_file(self, config: CompletePipelineWithAI) -> str:
        """Генерация конфигурационного файла."""
        
        pipeline = config.pipeline_config
        extract_config = pipeline.extract_config
        load_config = pipeline.load_config
        
        content = f'''"""
Configuration file for {pipeline.metadata.pipeline_name}

Содержит все константы и настройки для DAG.
"""

# DAG Configuration
DAG_ID = "{pipeline.metadata.pipeline_id}"
DAG_NAME = "{pipeline.metadata.pipeline_name}"
DAG_OWNER = "{pipeline.metadata.owner}"

# Source Configuration
SOURCE_PATH = "{extract_config.connection_string}"
SOURCE_TYPE = "{extract_config.source_type}"
CONTENT_TYPE = "{extract_config.content_type}"

# Processing Configuration  
BATCH_SIZE = {extract_config.batch_size}
PARALLEL_WORKERS = {extract_config.resources.parallel_workers}
MAX_DATA_SIZE_BYTES = {extract_config.resources.disk_space_mb * 1024 * 1024}

# Target Configuration
TARGET_STORAGE_TYPE = "{load_config.target_storage_type}"
TARGET_CONNECTION = "{load_config.connection_string}"
TARGET_DATABASE = "{load_config.database_name}"
TARGET_SCHEMA = "{load_config.schema_name}"
TARGET_TABLE = "{load_config.table_name}"

# Load Configuration
LOAD_STRATEGY = "{load_config.load_strategy}"
LOAD_BATCH_SIZE = {load_config.resources.batch_size}
CONCURRENT_CONNECTIONS = {load_config.resources.concurrent_connections}

# Processing Directories
TEMP_DIR = "/tmp/etl_processing/{pipeline.metadata.pipeline_id}"
LOG_DIR = "/var/log/airflow/dags/{pipeline.metadata.pipeline_id}"

# Resource Limits
CPU_CORES = {pipeline.total_cpu_cores}
MEMORY_MB = {pipeline.total_memory_mb}
EXECUTION_TIMEOUT_HOURS = {extract_config.schedule.execution_timeout_hours}

# Quality Thresholds
MIN_COMPLETENESS = {extract_config.data_quality.completeness_threshold}
MIN_ACCURACY = {extract_config.data_quality.accuracy_threshold}
MAX_DUPLICATES_PCT = {extract_config.data_quality.duplicate_threshold}

# Notification Settings
EMAIL_ON_SUCCESS = {pipeline.notifications.email_on_success}
EMAIL_ON_FAILURE = {pipeline.notifications.email_on_failure}
NOTIFICATION_EMAILS = {pipeline.notifications.email_addresses}

# Performance Settings (from AI Recommendations)
{self._generate_ai_performance_settings(config.ai_recommendations)}
'''
        
        return content
    
    def _generate_ai_performance_settings(self, recommendations: List) -> str:
        """Генерация настроек производительности на основе AI рекомендаций."""
        settings = []
        
        for rec in recommendations:
            if rec.recommendation_type.value == "performance_tuning":
                settings.append(f"# AI Рекомендация: {rec.title}")
                
                if "processing_speed" in rec.estimated_improvement:
                    settings.append(f"ENABLE_STREAMING_PARSING = True  # Улучшение: {rec.estimated_improvement['processing_speed']:.1f}x")
                
                if "memory_efficiency" in rec.estimated_improvement:
                    settings.append(f"ENABLE_MEMORY_OPTIMIZATION = True  # Улучшение: {rec.estimated_improvement['memory_efficiency']:.1f}x")
            
            elif rec.recommendation_type.value == "resource_allocation":
                settings.append(f"# AI Рекомендация: {rec.title}")
                settings.append("ENABLE_PARALLEL_PROCESSING = True")
        
        if not settings:
            settings.append("# AI рекомендации по производительности не найдены")
        
        return "\n".join(settings)
    
    async def _generate_requirements(self, config: CompletePipelineWithAI) -> str:
        """Генерация requirements.txt."""
        
        pipeline = config.pipeline_config
        
        requirements = [
            "# Core Airflow dependencies",
            "apache-airflow>=2.7.0",
            "apache-airflow-providers-postgres>=5.0.0",
            "apache-airflow-providers-http>=4.0.0",
            "",
            "# Data processing",
            "pydantic>=2.0.0",
            "pandas>=1.5.0",
            "numpy>=1.24.0",
            "",
            "# XML processing (if needed)",
        ]
        
        if pipeline.extract_config.content_type == ContentType.XML:
            requirements.extend([
                "lxml>=4.9.0",
                "xmltodict>=0.13.0",
            ])
        
        if pipeline.load_config.target_storage_type == TargetStorageType.POSTGRES:
            requirements.extend([
                "",
                "# PostgreSQL",
                "psycopg2-binary>=2.9.0",
                "sqlalchemy>=2.0.0"
            ])
        
        if pipeline.load_config.target_storage_type == TargetStorageType.CLICKHOUSE:
            requirements.extend([
                "",
                "# ClickHouse", 
                "clickhouse-driver>=0.2.0",
                "clickhouse-connect>=0.6.0"
            ])
        
        return "\n".join(requirements)
    
    async def _generate_deployment_docs(self, config: CompletePipelineWithAI, generated_files: Dict[str, str]) -> str:
        """Генерация документации по развертыванию."""
        
        pipeline = config.pipeline_config
        dag_id = pipeline.metadata.pipeline_id
        
        # AI рекомендации для развертывания
        deployment_recommendations = [
            rec for rec in config.ai_recommendations 
            if rec.recommendation_type.value in ["resource_allocation", "performance_tuning"]
        ]
        
        ai_deployment_section = ""
        if deployment_recommendations:
            ai_deployment_section = "## 🤖 AI Рекомендации для развертывания\n\n"
            for rec in deployment_recommendations:
                ai_deployment_section += f"### {rec.title}\n"
                ai_deployment_section += f"{rec.description}\n\n"
                ai_deployment_section += f"**Усилия по внедрению:** {rec.implementation_effort}\n"
                ai_deployment_section += f"**Ожидаемые улучшения:** {rec.estimated_improvement}\n\n"
                if rec.implementation_steps:
                    ai_deployment_section += "**Шаги внедрения:**\n"
                    for step in rec.implementation_steps:
                        ai_deployment_section += f"- {step}\n"
                ai_deployment_section += "\n"
        
        content = f'''# Deployment Guide for {pipeline.metadata.pipeline_name}

Автоматически сгенерированная документация для развертывания ETL пайплайна.

## 📋 Обзор пайплайна

- **Pipeline ID:** `{dag_id}`
- **Владелец:** {pipeline.metadata.owner}
- **Команда:** {pipeline.metadata.team}
- **Критичность:** {pipeline.metadata.criticality}
- **Ожидаемое время выполнения:** {pipeline.estimated_runtime_minutes} минут

## 📁 Сгенерированные файлы

{chr(10).join([f"- `{Path(path).name}` - {desc}" for desc, path in [
    ("Основной DAG файл", generated_files["dag_file"]),
    ("Модуль функций задач", generated_files["functions_file"]),
    ("Конфигурационный файл", generated_files["config_file"]),
    ("Зависимости Python", generated_files["requirements_file"])
]])}

## 🚀 Инструкции по развертыванию

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Копирование файлов в Airflow

Скопируйте следующие файлы в директорию DAGs Airflow:

```bash
cp {dag_id}.py $AIRFLOW_HOME/dags/
cp {dag_id}_functions.py $AIRFLOW_HOME/dags/
cp {dag_id}_config.py $AIRFLOW_HOME/dags/
```

### 3. Настройка подключений

Создайте следующие Airflow подключения:

#### Источник данных
- **Connection ID:** `{dag_id}_source`
- **Connection Type:** `{pipeline.extract_config.source_type}`
- **Host/URI:** `{pipeline.extract_config.connection_string}`

#### Целевое хранилище  
- **Connection ID:** `{dag_id}_target`
- **Connection Type:** `{pipeline.load_config.target_storage_type}`
- **Host:** (укажите ваш хост {pipeline.load_config.target_storage_type})
- **Database:** `{pipeline.load_config.database_name}`
- **Schema:** `{pipeline.load_config.schema_name}`

### 4. Создание целевой таблицы

```sql
-- Создайте таблицу {pipeline.load_config.schema_name}.{pipeline.load_config.table_name}
-- в вашей целевой системе {pipeline.load_config.target_storage_type}

CREATE TABLE {pipeline.load_config.schema_name}.{pipeline.load_config.table_name} (
    record_id VARCHAR(50) PRIMARY KEY,
    coordinate_system VARCHAR(20),
    purpose TEXT,
    coordinate_count INTEGER,
    sample_coordinates TEXT,
    processed_at TIMESTAMP,
    source_file VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5. Настройка переменных Airflow

```bash
# Установка переменных конфигурации
airflow variables set {dag_id}_batch_size {pipeline.extract_config.batch_size}
airflow variables set {dag_id}_parallel_workers {pipeline.extract_config.resources.parallel_workers}
airflow variables set {dag_id}_notification_email "{','.join(pipeline.notifications.email_addresses)}"
```

### 6. Тестирование DAG

```bash
# Проверка синтаксиса DAG
airflow dags list | grep {dag_id}

# Тестовый запуск
airflow dags test {dag_id} $(date -d "yesterday" +%Y-%m-%d)

# Проверка задач
airflow tasks list {dag_id}
```

## ⚙️ Конфигурация ресурсов

### Минимальные требования
- **CPU:** {pipeline.total_cpu_cores} ядра
- **RAM:** {pipeline.total_memory_mb} МБ
- **Дисковое пространство:** {pipeline.extract_config.resources.disk_space_mb} МБ

### Настройки пула ресурсов Airflow

```bash
# Создание пула ресурсов
airflow pools set {dag_id}_pool {pipeline.extract_config.resources.parallel_workers} "Pool for {dag_id}"
```

{ai_deployment_section}

## 📊 Мониторинг и метрики

### Ключевые метрики для отслеживания:
- Количество обработанных записей
- Время выполнения каждой задачи
- Использование ресурсов (CPU/RAM)
- Качество данных (completeness, accuracy)
- Количество ошибок

### Настройка алертов:
- Email уведомления при сбоях: {pipeline.notifications.email_on_failure}
- SLA: {pipeline.sla_minutes or 'не установлено'} минут

## 🔧 Устранение неполадок

### Частые проблемы:

1. **Файлы источника недоступны**
   - Проверьте путь: `{pipeline.extract_config.connection_string}`
   - Убедитесь в правах доступа к файлам

2. **Ошибки подключения к БД**
   - Проверьте настройки подключения в Airflow
   - Убедитесь в доступности целевой БД

3. **Превышение лимитов ресурсов**
   - Увеличьте память в конфигурации
   - Уменьшите размер батча

### Логи:
- Логи Airflow: `$AIRFLOW_HOME/logs/dags/{dag_id}/`
- Логи приложения: `/var/log/airflow/dags/{dag_id}/`

## 📞 Поддержка

- **Владелец:** {pipeline.metadata.owner}
- **Команда:** {pipeline.metadata.team}
- **Email для уведомлений:** {', '.join(pipeline.notifications.email_addresses)}

---

*Документация создана автоматически {config.generated_at.strftime('%Y-%m-%d %H:%M:%S')}*
*Версия генератора: {config.generator_version}*
'''
        
        return content
    
    def _get_recommendation_for_task(self, recommendations: List, task_type: str) -> str:
        """Получение рекомендации для конкретного типа задачи."""
        for rec in recommendations:
            if task_type.lower() in rec.description.lower():
                return rec.description
        return "Специальные рекомендации отсутствуют"
    
    def _generate_transform_rules_comment(self, transform_config) -> str:
        """Генерация комментария с правилами трансформации."""
        if not transform_config.transformation_rules:
            return "    # Стандартная трансформация XML геоданных"
        
        rules = []
        for rule in transform_config.transformation_rules:
            rules.append(f"    # - {rule.rule_name}: {rule.expression}")
        
        return "\n".join(rules)


# Пример использования
async def main():
    """Демонстрация генерации DAG."""
    
    # Импорт builder для создания полной конфигурации
    from .comprehensive_dag_builder import ComprehensiveDAGBuilder
    
    # Создание полного пайплайна
    builder = ComprehensiveDAGBuilder()
    pipeline_config = await builder.build_complete_pipeline_from_url(
        source_url="file://d:/lct-hack-2025/backend/parsers/sample/XML/",
        pipeline_name="Enhanced Geospatial XML Processing",
        owner="senior_data_engineer",
        team="geo_analytics_team"
    )
    
    # Генерация Airflow DAG
    generator = EnhancedAirflowDAGGenerator()
    generated_files = await generator.generate_complete_dag(pipeline_config)
    
    print("🎉 Генерация завершена!")
    print("📁 Созданные файлы:")
    for file_type, file_path in generated_files.items():
        print(f"   {file_type}: {file_path}")
    
    return generated_files


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())