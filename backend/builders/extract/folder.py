"""Folder extract configuration builder."""

import json
import logging
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import pandas as pd
from ydata_profiling import ProfileReport

from models.extract import Attribute, Content, ContentType, PostgreSqlDataType, Source
from parsers.xml_parser import XMLParser

from .base import BaseExtractConfigBuilder


class FolderExtractConfigBuilder(BaseExtractConfigBuilder):
    """Builder for folder source configurations.

    Extracts metadata from folder sources.
    """

    @classmethod
    async def get_content_metadata(cls, source: Source) -> Content:
        """Extract content metadata from folder source."""
        try:
            folder_path = Path(source.connection_string.replace("//", "").replace("file:", ""))

            if not folder_path.exists():
                return Content(message_name="empty_folder", metamodel=[])

            # Определяем тип содержимого
            content_type = await cls.get_src_content_type(source)

            if content_type == ContentType.xml:
                return await cls._analyze_xml_folder(folder_path)
            elif content_type == ContentType.csv:
                return await cls._convert_csv_analysis_to_metamodel(folder_path)
            else:
                return Content(
                    message_name=folder_path.name, is_complex_nesting_present=False, metamodel=[]
                )

        except Exception as e:
            print(f"Ошибка анализа папки: {e}")
            logging.getLogger(__name__).error(f"Ошибка анализа папки: {e}")
            return Content(message_name="error_folder", metamodel=[])

    @classmethod
    async def _analyze_xml_folder(cls, folder_path: Path) -> Content:
        """Анализ XML файлов в папке с использованием полноценного парсера."""
        xml_files = list(folder_path.glob("*.xml"))

        if not xml_files:
            return Content(message_name="no_xml_files", metamodel=[])

        try:
            print(f"📊 Анализирую XML папку: {folder_path}")
            print(f"📄 Найдено XML файлов: {len(xml_files)}")

            # Используем полноценный XML парсер
            xml_parser = XMLParser(max_sample_values=20)
            analysis, processed_files = xml_parser.analyze_xml_folder(folder_path)

            print(f"✅ Обработано файлов: {len(processed_files)}")
            print(f"🔍 Найдено уникальных полей: {analysis.unique_elements}")
            print(f"📈 Оценка записей: {analysis.total_records}")
            print(f"📏 Максимальная глубина: {analysis.max_depth}")

            # Преобразуем результаты анализа в атрибуты
            attributes = xml_parser.convert_to_extract_attributes(analysis)

            # Определяем сложность вложенности
            is_complex = analysis.max_depth > 3 or analysis.unique_elements > 20

            return Content(
                message_name=f"xml_files_{len(xml_files)}",
                is_complex_nesting_present=is_complex,
                metamodel=attributes,
            )

        except Exception as e:
            print(f"❌ Ошибка анализа XML структуры: {e}")
            logging.getLogger(__name__).error(f"❌ Ошибка анализа XML структуры: {e}")
            # Fallback на простой анализ
            return await cls._analyze_xml_folder_simple(folder_path)

    @classmethod
    async def _analyze_xml_folder_simple(cls, folder_path: Path) -> Content:
        """Простой анализ XML файлов как fallback."""
        xml_files = list(folder_path.glob("*.xml"))

        if not xml_files:
            return Content(message_name="no_xml_files", metamodel=[])

        # Анализируем первый XML файл для получения базовой структуры
        sample_file = xml_files[0]
        attributes = []

        try:
            tree = ET.parse(sample_file)
            root = tree.getroot()

            order = 1
            analyzed_tags = set()

            # Рекурсивно проходим по XML структуре
            for elem in root.iter():
                if elem.tag not in analyzed_tags and elem.text and elem.text.strip():
                    attr = Attribute(
                        order_no=order,
                        column_name=elem.tag.replace(":", "_").replace("-", "_"),
                        data_type=cls._detect_xml_data_type(elem.text.strip()),
                        is_nullable=True,
                        character_maximum_length=255,
                        numeric_precision=10,
                        numeric_scale=0,
                    )
                    attributes.append(attr)
                    analyzed_tags.add(elem.tag)
                    order += 1

                    if order > 50:  # Ограничиваем для производительности
                        break

            return Content(
                message_name=f"xml_files_{len(xml_files)}_simple",
                is_complex_nesting_present=True,
                metamodel=attributes,
            )

        except Exception as e:
            print(f"❌ Ошибка простого анализа XML: {e}")
            logging.getLogger(__name__).error(f"❌ Ошибка простого анализа XML: {e}")
            return Content(
                message_name="xml_analysis_error", is_complex_nesting_present=True, metamodel=[]
            )

    @classmethod
    def _detect_xml_data_type(cls, value: str) -> PostgreSqlDataType:
        """Определение типа данных из XML значения."""
        try:
            # Пытаемся определить тип
            if value.lower() in ["true", "false"]:
                return PostgreSqlDataType.BOOLEAN

            # Пробуем число
            if "." in value:
                float(value)
                return PostgreSqlDataType.NUMERIC
            else:
                int(value)
                return PostgreSqlDataType.INTEGER

        except ValueError:
            pass

        # По умолчанию текст
        return PostgreSqlDataType.TEXT

    @classmethod
    async def get_src_content_type(cls, source: Source) -> ContentType:
        """Get content type for folder source.

        Args:
            source: Folder source configuration.

        Returns:
            ContentType for folder.
        """
        try:
            folder_path = Path(source.connection_string.replace("//", "").replace("file:", ""))

            if not folder_path.exists():
                return ContentType.na

            # Проверяем типы файлов в папке
            xml_files = list(folder_path.glob("*.xml"))
            json_files = list(folder_path.glob("*.json"))
            csv_files = list(folder_path.glob("*.csv"))

            if xml_files:
                return ContentType.xml
            elif json_files:
                return ContentType.json
            elif csv_files:
                return ContentType.csv
            else:
                return ContentType.na

        except Exception:
            return ContentType.na

    @classmethod
    async def get_content_statistics(cls, source: Source) -> dict:
        """Retrieve statistics about the source content.

        Args:
            source: The source configuration.

        Returns:
            Dictionary containing content statistics with
            any additional information about the source.
        """
        try:
            folder_path = Path(source.connection_string.replace("//", "").replace("file:", ""))

            if not folder_path.exists():
                return {"error": "Folder not found", "total_files": 0, "total_size_mb": 0}

            # Собираем статистику по файлам
            all_files = list(folder_path.glob("*.*"))
            xml_files = list(folder_path.glob("*.xml"))
            json_files = list(folder_path.glob("*.json"))
            csv_files = list(folder_path.glob("*.csv"))

            total_size_bytes = sum(f.stat().st_size for f in all_files if f.is_file())

            stats = {
                "total_files": len(all_files),
                "xml_files": len(xml_files),
                "json_files": len(json_files),
                "csv_files": len(csv_files),
                "total_size_mb": total_size_bytes / (1024 * 1024),
                "avg_file_size_mb": (total_size_bytes / len(all_files) / (1024 * 1024))
                if all_files
                else 0,
                "folder_path": str(folder_path),
                "source_type": "folder",
            }

            # Дополнительная статистика для XML файлов
            if xml_files:
                xml_size_bytes = sum(f.stat().st_size for f in xml_files)
                stats.update(
                    {
                        "xml_total_size_mb": xml_size_bytes / (1024 * 1024),
                        "xml_avg_size_mb": xml_size_bytes / len(xml_files) / (1024 * 1024),
                        "estimated_xml_records": cls._estimate_xml_records(xml_files),
                    }
                )
            elif csv_files:
                # Analyze the first CSV file
                first_csv_file = csv_files[0]
                analysis_result = await cls._analyze_csv_file(first_csv_file)

                if "error" in analysis_result:
                    return {
                        "error": analysis_result["error"],
                        "folder_path": folder_path,
                        "status": "analysis_failed",
                    }

                # Create statistics in the expected format
                stats = {
                    "file_analyzed": os.path.basename(first_csv_file),
                    "total_files": len(csv_files),
                    "file_types": ["csv"],
                    "analysis_summary": {
                        "row_count": analysis_result.get("row_count", 0),
                        "column_count": len(analysis_result.get("columns", [])),
                        "file_size": analysis_result.get("file_size", 0),
                        "variables": analysis_result.get("variables", 0),
                    },
                }
            return stats

        except Exception as e:
            logging.getLogger(__name__).error(f"Error getting statistics for {folder_path}: {e}")
            print(f"Ошибка получения статистики папки: {e}")
            return {"error": str(e), "total_files": 0, "total_size_mb": 0, "source_type": "folder"}

    @classmethod
    def _estimate_xml_records(cls, xml_files: list) -> int:
        """Оценка количества записей в XML файлах."""
        try:
            if not xml_files:
                return 0

            # Используем XML парсер для более точной оценки
            from parsers.xml_parser import XMLParser

            xml_parser = XMLParser()

            total_records = 0
            sample_count = min(3, len(xml_files))  # Анализируем до 3 файлов

            for xml_file in xml_files[:sample_count]:
                try:
                    analysis = xml_parser.analyze_xml_file(xml_file)
                    total_records += analysis.total_records
                except Exception:
                    # Fallback для отдельного файла
                    tree = ET.parse(xml_file)
                    root = tree.getroot()
                    records_in_file = len(
                        [elem for elem in root.iter() if elem.text and elem.text.strip()]
                    )
                    total_records += records_in_file

            # Экстраполируем на все файлы
            if sample_count > 0:
                avg_records_per_file = total_records / sample_count
                total_estimated = int(avg_records_per_file * len(xml_files))
            else:
                total_estimated = len(xml_files) * 1000

            return total_estimated

        except Exception as e:
            print(f"⚠️ Ошибка оценки XML записей: {e}")
            logging.getLogger(__name__).error(f"⚠️ Ошибка оценки XML записей: {e}")
            # Fallback оценка
            return len(xml_files) * 1000

    @classmethod
    async def _convert_csv_analysis_to_metamodel(cls, folder_path: Path) -> Content:
        """Convert CSV analysis result to Content type."""
        csv_files = list(folder_path.glob("*.csv"))

        if not csv_files:
            return Content(message_name="no_csv_files", metamodel=[])

        try:
            print(f"📊 Анализирую CSV папку: {folder_path}")
            print(f"📄 Найдено CSV файлов: {len(csv_files)}")

            # Анализируем первый CSV файл
            first_csv_file = csv_files[0]
            analysis_result = await cls._analyze_csv_file(first_csv_file)

            if "error" in analysis_result:
                print(f"❌ Ошибка анализа CSV файла: {analysis_result['error']}")
                return Content(
                    message_name="csv_analysis_error",
                    is_complex_nesting_present=False,
                    metamodel=[],
                )

            # Преобразуем результат анализа в атрибуты
            attributes = []
            order = 1

            # Получаем информацию о переменных из анализа
            variables = analysis_result.get("variables", {})
            columns = analysis_result.get("columns", [])

            for column_name in columns:
                var_info = variables.get(column_name, {})

                # Определяем тип данных
                data_type = cls._detect_csv_data_type(var_info, column_name)

                # Определяем максимальную длину для строковых типов
                char_max_length = 255  # Значение по умолчанию
                if data_type in [PostgreSqlDataType.TEXT, PostgreSqlDataType.VARCHAR]:
                    char_max_length = var_info.get("max_length", 255)
                    # Убеждаемся, что значение валидное
                    if char_max_length is None or char_max_length <= 0:
                        char_max_length = 255

                # Определяем точность для числовых типов
                numeric_precision = 10  # Значение по умолчанию
                numeric_scale = 0  # Значение по умолчанию

                if data_type in [PostgreSqlDataType.NUMERIC, PostgreSqlDataType.DECIMAL]:
                    numeric_precision = 10
                    numeric_scale = 2
                elif data_type == PostgreSqlDataType.INTEGER:
                    numeric_precision = 10
                    numeric_scale = 0

                # Для нечисловых типов оставляем значения по умолчанию

                attr = Attribute(
                    order_no=order,
                    column_name=column_name.replace(" ", "_").replace("-", "_").lower(),
                    data_type=data_type,
                    is_nullable=var_info.get("n_missing", 0) > 0,
                    character_maximum_length=char_max_length,
                    numeric_precision=numeric_precision,
                    numeric_scale=numeric_scale,
                )
                attributes.append(attr)
                order += 1

            print(f"✅ Проанализировано колонок: {len(attributes)}")
            # Исправленная строка - убрал .value, так как data_type уже строка
            print(f"📊 Типы данных: {[attr.data_type for attr in attributes]}")

            # CSV обычно не имеет сложной вложенности
            is_complex = len(attributes) > 20  # Считаем сложным если много колонок

            return Content(
                message_name=f"csv_files_{len(csv_files)}",
                is_complex_nesting_present=is_complex,
                metamodel=attributes,
            )

        except Exception as e:
            print(f"❌ Ошибка анализа CSV: {e}")
            logging.getLogger(__name__).error(f"❌ Ошибка анализа CSV: {e}")
            return Content(
                message_name="csv_analysis_error", is_complex_nesting_present=False, metamodel=[]
            )

    @classmethod
    def _detect_csv_data_type(cls, var_info: dict, column_name: str) -> PostgreSqlDataType:
        """Определение типа данных CSV на основе анализа переменных."""
        try:
            var_type = var_info.get("type", "").lower()
            distinct_count = var_info.get("n_distinct", 0)

            # Анализируем тип из профилирования данных
            if var_type == "numeric":
                # Для числовых типов проверяем, целое или с плавающей точкой
                if var_info.get("fraction", 0) > 0:  # Если есть дробная часть
                    return PostgreSqlDataType.NUMERIC
                else:
                    return PostgreSqlDataType.INTEGER

            elif var_type == "boolean" or distinct_count == 2:
                # Проверяем, действительно ли это булево значение
                # Смотрим на уникальные значения
                value_counts = var_info.get("value_counts", {})
                if len(value_counts) == 2:
                    keys = list(value_counts.keys())
                    # Проверяем, являются ли значения булевыми
                    if all(
                        str(key).lower() in ["true", "false", "1", "0", "yes", "no"] for key in keys
                    ):
                        return PostgreSqlDataType.BOOLEAN
                return PostgreSqlDataType.VARCHAR  # Если не булево, то текст

            elif var_type == "datetime":
                return PostgreSqlDataType.TIMESTAMP

            elif var_type == "categorical":
                # Для категориальных данных используем VARCHAR
                return PostgreSqlDataType.VARCHAR

            else:
                # Эвристики на основе имени колонки и данных
                column_lower = column_name.lower()

                # Сначала проверяем по имени колонки
                if any(
                    keyword in column_lower
                    for keyword in ["id", "code", "num", "count", "index", "number"]
                ):
                    # Проверяем, действительно ли это число
                    if var_type == "numeric":
                        return PostgreSqlDataType.INTEGER
                    else:
                        # Пытаемся определить, можно ли преобразовать в число
                        try:
                            # Проверяем примеры значений
                            value_counts = var_info.get("value_counts", {})
                            if value_counts:
                                sample_value = list(value_counts.keys())[0]
                                float(str(sample_value))  # Пробуем преобразовать
                                return PostgreSqlDataType.INTEGER
                        except (ValueError, TypeError):
                            pass
                        return PostgreSqlDataType.VARCHAR

                elif any(
                    keyword in column_lower
                    for keyword in ["amount", "price", "cost", "rate", "percent", "ratio", "value"]
                ):
                    if var_type == "numeric":
                        return PostgreSqlDataType.NUMERIC
                    else:
                        return PostgreSqlDataType.VARCHAR

                elif any(
                    keyword in column_lower
                    for keyword in ["flag", "is_", "has_", "active", "enabled", "status"]
                ):
                    if distinct_count <= 3:  # Малое количество уникальных значений
                        return PostgreSqlDataType.BOOLEAN
                    else:
                        return PostgreSqlDataType.VARCHAR

                elif any(
                    keyword in column_lower
                    for keyword in ["date", "time", "created", "updated", "timestamp"]
                ):
                    return PostgreSqlDataType.TIMESTAMP

                else:
                    if var_type == "numeric":
                        return PostgreSqlDataType.INTEGER
                    elif distinct_count <= 40:  # Категориальные данные
                        return PostgreSqlDataType.VARCHAR
                    else:
                        return PostgreSqlDataType.TEXT

        except Exception as e:
            print(f"⚠️ Ошибка определения типа для {column_name}: {e}")
            return PostgreSqlDataType.VARCHAR

    @classmethod
    async def _analyze_csv_file(cls, file_path: Path) -> dict[str, Any]:
        """Analyze CSV file with improved type detection."""
        try:
            sample_size = 10000
            separators = [",", ";", "\t", "|"]

            for sep in separators:
                try:
                    df = pd.read_csv(
                        file_path, sep=sep, on_bad_lines="skip", engine="python", nrows=sample_size
                    )
                    if df.shape[1] > 1:
                        break
                except Exception as e:
                    logging.getLogger(__name__).warning(
                        f"Failed to read CSV file {file_path} with separator '{sep}': {e}"
                    )
                    continue
            else:
                sep = ","
                df = pd.read_csv(
                    file_path, sep=sep, on_bad_lines="skip", engine="python", nrows=sample_size
                )

            # Create profile
            profile = ProfileReport(df, title="Profiling Report", explorative=True)
            profile_json = profile.to_json()
            data = json.loads(profile_json)
            cleaned_data = cls._clean_profile_data(data)

            return {
                "variables": cleaned_data.get("variables", {}),
                "table": data.get("table", {}),
                "columns": list(df.columns),
                "row_count": len(df),
                "file_size": os.path.getsize(file_path),
                "file_name": os.path.basename(file_path),
            }

        except Exception as e:
            logging.getLogger(__name__).error(f"Error analyzing CSV file {file_path}: {e}")
            return {"error": str(e)}

    @classmethod
    def _clean_profile_data(cls, profile_data: dict, exclude_keys: list[str] | None = None) -> dict:
        """Recursively remove specified keys from profile data."""
        if exclude_keys is None:
            exclude_keys = [
                "value_counts_without_nan",
                "value_counts_index_sorted",
                "value_counts",
                "value_counts_with_nan",
                "histogram_data",
                "histogram_frequency",
                "mini_histogram",
                "first_rows",
                "length_histogram",
                "histogram_length",
                "bin_edges",
                "character_counts",
                "category_alias_values",
                "block_alias_values",
                "block_alias_char_counts",
                "script_char_counts",
                "category_alias_char_counts",
                "word_counts",
                "histogram",
                "counts",
                "block_alias_counts",
                "category_alias_counts",
                "script_counts",
                "n_scripts",
                "n_characters_distinct",
            ]

        if isinstance(profile_data, dict):
            return {
                key: cls._clean_profile_data(value, exclude_keys)
                for key, value in profile_data.items()
                if key not in exclude_keys
            }
        elif isinstance(profile_data, list):
            return [cls._clean_profile_data(item, exclude_keys) for item in profile_data]
        else:
            return profile_data
