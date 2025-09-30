"""Folder extract configuration builder."""

import xml.etree.ElementTree as ET
from pathlib import Path

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
            else:
                return Content(
                    message_name=folder_path.name, is_complex_nesting_present=False, metamodel=[]
                )

        except Exception as e:
            print(f"Ошибка анализа папки: {e}")
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

            return stats

        except Exception as e:
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
            # Fallback оценка
            return len(xml_files) * 1000
