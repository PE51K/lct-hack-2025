"""
ETL pipeline for xml data processing

Автоматически сгенерированный Airflow DAG
Pipeline ID: etl_full_xml_test_pipeline
Создан: 2025-09-30T22:03:49.878752
Версия генератора: 2.0.0

Ожидаемое время выполнения: 13 минут
Требования CPU: 1.0 ядер
Требования RAM: 1824 МБ

# AI РЕКОМЕНДАЦИИ ПО ОПТИМИЗАЦИИ:
# 1. PostgreSQL подходит для небольших объемов данных
#    Для объемов данных менее 100K записей PostgreSQL обеспечит отличную производительность с меньшими затратами на инфраструктуру.
#    Уверенность: 92%
#    Воздействие: medium
#    Улучшения: cost_reduction: 0.4x, maintenance_simplicity: 0.8x
#
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.email import EmailOperator
from airflow.sensors.filesystem import FileSensor
import logging
import json
from pathlib import Path
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
# Для работы с файловой системой импорты уже включены

# Импорт конфигурации и функций
from etl_full_xml_test_pipeline_config import *
from etl_full_xml_test_pipeline_functions import *


default_args = {
    "owner": "test_user",
    "depends_on_past": False,
    "start_date": datetime(2025, 9, 30),
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(hours=2),
    "email": ['test_user@company.com'],
}

dag = DAG(
    DAG_ID,
    default_args=default_args,
    description="ETL pipeline for xml data processing",
    schedule_interval="@daily",
    start_date=datetime(2025, 9, 30),
    catchup=False,
    max_active_runs=1,
    tags=['xml', 'folder', 'etl', 'automated']
)


# Стартовая задача
start_task = DummyOperator(
    task_id="start_pipeline",
    dag=dag
)

# Валидация источника данных
validate_source_task = PythonOperator(
    task_id="validate_source",
    python_callable=validate_source_data,
    provide_context=True,
    dag=dag
)

# Извлечение данных
extract_task = PythonOperator(
    task_id="extract_data",
    python_callable=extract_data,
    provide_context=True,
    pool_slots=2,
    dag=dag
)

# Трансформация данных  
transform_task = PythonOperator(
    task_id="transform_data",
    python_callable=transform_data,
    provide_context=True,
    dag=dag
)

# Валидация трансформированных данных
validate_transform_task = PythonOperator(
    task_id="validate_transformed_data", 
    python_callable=validate_transformed_data,
    provide_context=True,
    dag=dag
)

# Загрузка в PostgreSQL
load_task = PythonOperator(
    task_id="load_to_postgres",
    python_callable=load_to_postgres,
    provide_context=True,
    pool_slots=5,
    dag=dag
)

# Валидация загруженных данных
validate_load_task = PythonOperator(
    task_id="validate_loaded_data",
    python_callable=validate_loaded_data,
    provide_context=True,
    dag=dag
)

# Очистка временных файлов
cleanup_task = PythonOperator(
    task_id="cleanup_temp_files",
    python_callable=cleanup_temp_files,
    provide_context=True,
    trigger_rule="all_done",
    dag=dag
)

# Финальная задача
end_task = DummyOperator(
    task_id="end_pipeline",
    trigger_rule="none_failed_min_one_success",
    dag=dag
)

# Зависимости задач
start_task >> validate_source_task >> extract_task
extract_task >> transform_task >> validate_transform_task
validate_transform_task >> load_task >> validate_load_task
validate_load_task >> success_notification >> end_task
[validate_load_task, success_notification] >> cleanup_task >> end_task
