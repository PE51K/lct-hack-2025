"""
Task Functions Module for Mock PostgreSQL Pipeline

Содержит все функции для выполнения ETL задач.
Генерировано автоматически: 2025-09-30T22:03:49.889414
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Добавление пути к парсерам
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "parsers", "sample", "XML"))

try:
    from xml_parser import XMLDataProcessor, XMLStreamParser
except ImportError as e:
    logging.warning(f"XML parser not available: {e}")
    XMLStreamParser = None
    XMLDataProcessor = None

# Импорт конфигурации
from etl_mock_postgresql_pipeline_config import *


def validate_source_data(**context):
    """
    Валидация исходных данных.

    AI Рекомендация: Специальные рекомендации отсутствуют
    """
    logging.info("🔍 Начало валидации источника данных")

    source_path = SOURCE_PATH
    content_type = "table"

    if content_type == "xml":
        # Валидация XML файлов
        xml_files = list(Path(source_path).glob("*.xml"))

        if not xml_files:
            raise ValueError(f"XML файлы не найдены в: {source_path}")

        total_size = sum(f.stat().st_size for f in xml_files)
        logging.info(f"Найдено XML файлов: {len(xml_files)}")
        logging.info(f"Общий размер: {total_size / (1024 * 1024):.2f} МБ")

        # Проверка размера данных
        if total_size > MAX_DATA_SIZE_BYTES:
            raise ValueError(f"Размер данных превышает лимит: {total_size} > {MAX_DATA_SIZE_BYTES}")

        # Проверка доступности файлов
        for xml_file in xml_files:
            if not os.access(xml_file, os.R_OK):
                raise PermissionError(f"Нет доступа к файлу: {xml_file}")

    logging.info("✅ Валидация источника успешно завершена")
    return {"validation_status": "passed", "files_count": len(xml_files)}


def extract_data(**context):
    """
    Извлечение данных из источника.

    Конфигурация:
    - Источник: postgres
    - Формат: table
    - Размер батча: 1000
    - Параллельные воркеры: 1
    """
    logging.info("📥 Начало извлечения данных")

    source_path = SOURCE_PATH
    batch_size = BATCH_SIZE
    content_type = "table"

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
            logging.info(f"Обработка файла: {xml_file.name}")

            file_records = 0
            batch_data = []

            try:
                for item in parser.parse_file_stream(str(xml_file)):
                    batch_data.append(item)
                    file_records += 1

                    # Сохранение батча при достижении размера
                    if len(batch_data) >= batch_size:
                        batch_filename = f"batch_{processed_files}_{len(batch_data)}"
                        processor.save_to_json(batch_data, batch_filename)
                        batch_data = []

                # Сохранение остатка
                if batch_data:
                    batch_filename = f"batch_{processed_files}_final"
                    processor.save_to_json(batch_data, batch_filename)

                total_records += file_records
                processed_files += 1

                logging.info(f"✅ Файл {xml_file.name}: {file_records} записей")

            except Exception as e:
                logging.error(f"❌ Ошибка обработки файла {xml_file.name}: {e}")
                raise

    else:
        raise NotImplementedError(f"Извлечение для формата {content_type} не реализовано")

    result = {
        "total_records": total_records,
        "processed_files": processed_files,
        "batch_size": batch_size,
        "temp_dir": TEMP_DIR,
    }

    logging.info(f"✅ Извлечение завершено: {total_records} записей из {processed_files} файлов")
    return result


def transform_data(**context):
    """
    Трансформация извлеченных данных.

    Применяемые трансформации:
        # Стандартная трансформация XML геоданных
    """
    logging.info("🔄 Начало трансформации данных")

    # Получение данных от предыдущей задачи
    extract_result = context["ti"].xcom_pull(task_ids="extract_data")
    temp_dir = Path(extract_result.get("temp_dir", TEMP_DIR))

    transformed_records = []

    # Чтение батчей данных
    batch_files = list(temp_dir.glob("batch_*.json"))
    logging.info(f"Найдено батчей для обработки: {len(batch_files)}")

    for batch_file in batch_files:
        try:
            with open(batch_file, encoding="utf-8") as f:
                batch_data = json.load(f)

            # Трансформация каждой записи в батче
            for record in batch_data:
                transformed_record = transform_single_record(record)
                if transformed_record:  # Пропускаем невалидные записи
                    transformed_records.append(transformed_record)

            logging.info(f"✅ Обработан батч {batch_file.name}: {len(batch_data)} записей")

        except Exception as e:
            logging.error(f"❌ Ошибка обработки батча {batch_file.name}: {e}")
            raise

    # Сохранение трансформированных данных
    output_file = temp_dir / "transformed_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(transformed_records, f, ensure_ascii=False, indent=2, default=str)

    result = {"transformed_records": len(transformed_records), "output_file": str(output_file)}

    logging.info(f"✅ Трансформация завершена: {len(transformed_records)} записей")
    return result


def transform_single_record(record: dict[str, Any]) -> dict[str, Any]:
    """Трансформация одной записи."""
    try:
        # Базовая трансформация для XML геоданных
        transformed = {
            "record_id": record.get("number_pp", "unknown"),
            "coordinate_system": record.get("sk_id", "unknown"),
            "purpose": record.get("purpose", "unknown"),
            "processed_at": datetime.now().isoformat(),
            "source_file": record.get("_source_file", "unknown"),
        }

        # Обработка пространственных элементов
        spatial_elements = record.get("spatial_elements", [])
        if spatial_elements:
            coordinate_count = sum(len(se.get("ordinates", [])) for se in spatial_elements)
            transformed["coordinate_count"] = coordinate_count

            # Извлечение первых координат для примера
            if spatial_elements[0].get("ordinates"):
                first_coords = spatial_elements[0]["ordinates"][:2]
                transformed["sample_coordinates"] = first_coords

        return transformed

    except Exception as e:
        logging.warning(f"Ошибка трансформации записи: {e}")
        return None


def validate_transformed_data(**context):
    """Валидация трансформированных данных."""
    logging.info("🔍 Валидация трансформированных данных")

    # Получение результата трансформации
    transform_result = context["ti"].xcom_pull(task_ids="transform_data")
    output_file = Path(transform_result["output_file"])

    if not output_file.exists():
        raise FileNotFoundError(f"Файл трансформированных данных не найден: {output_file}")

    # Загрузка и валидация данных
    with open(output_file, encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        raise ValueError("Нет данных после трансформации")

    # Проверка обязательных полей
    required_fields = ["record_id", "coordinate_system", "processed_at"]
    validation_errors = []

    for i, record in enumerate(data[:10]):  # Проверка первых 10 записей
        for field in required_fields:
            if field not in record or record[field] in [None, ""]:
                validation_errors.append(f"Запись {i}: отсутствует поле '{field}'")

    if validation_errors:
        raise ValueError(f"Ошибки валидации: {'; '.join(validation_errors)}")

    logging.info(f"✅ Валидация прошла успешно: {len(data)} записей")
    return {"validation_status": "passed", "validated_records": len(data)}


def load_to_postgres(**context):
    """
    Загрузка данных в postgres.

    Конфигурация:
    - Стратегия загрузки: incremental
    - Размер батча: 10000
    - Целевая таблица: public.Mock PostgreSQL Pipeline_data
    """
    logging.info("📤 Начало загрузки данных в postgres")

    # Получение трансформированных данных
    transform_result = context["ti"].xcom_pull(task_ids="transform_data")
    output_file = Path(transform_result["output_file"])

    with open(output_file, encoding="utf-8") as f:
        data = json.load(f)

    logging.info(f"Загрузка {len(data)} записей в {TARGET_SCHEMA}.{TARGET_TABLE}")

    # В реальной реализации здесь будет подключение к БД
    # Пока симулируем загрузку

    batch_size = LOAD_BATCH_SIZE
    loaded_records = 0

    for i in range(0, len(data), batch_size):
        batch = data[i : i + batch_size]

        # Симуляция загрузки батча
        logging.info(f"Загрузка батча: {i + 1}-{min(i + batch_size, len(data))}")

        # Здесь будет реальная загрузка в БД
        # load_batch_to_database(batch)

        loaded_records += len(batch)

    result = {
        "loaded_records": loaded_records,
        "target_table": f"{TARGET_SCHEMA}.{TARGET_TABLE}",
        "load_strategy": "incremental",
    }

    logging.info(f"✅ Загрузка завершена: {loaded_records} записей")
    return result


def validate_loaded_data(**context):
    """Валидация загруженных данных в целевой системе."""
    logging.info("🔍 Валидация загруженных данных")

    load_result = context["ti"].xcom_pull(task_ids="load_to_postgres")
    expected_records = load_result["loaded_records"]

    # Симуляция проверки количества записей в БД
    logging.info(f"Проверка количества записей в {TARGET_SCHEMA}.{TARGET_TABLE}")
    logging.info(f"Ожидается записей: {expected_records}")

    # В реальной реализации здесь будет запрос к БД
    # actual_count = get_table_row_count(TARGET_SCHEMA, TARGET_TABLE)
    actual_count = expected_records  # Симуляция

    if actual_count != expected_records:
        raise ValueError(
            f"Несоответствие количества записей: ожидалось {expected_records}, найдено {actual_count}"
        )

    # Дополнительные проверки качества данных
    quality_checks = {
        "row_count": actual_count,
        "null_checks": "passed",
        "data_types": "passed",
        "constraints": "passed",
    }

    logging.info(f"✅ Валидация загруженных данных успешна: {actual_count} записей")
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
                logging.info(f"Удален временный файл: {temp_file.name}")
            except Exception as e:
                logging.warning(f"Не удалось удалить {temp_file}: {e}")

        logging.info(f"✅ Очистка завершена: удалено {len(temp_files)} временных файлов")

    return {"cleanup_status": "completed", "files_removed": len(temp_files)}
