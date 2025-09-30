"""
Полноценный XML парсер для анализа и извлечения метаданных из XML файлов.

Поддерживает:
- Анализ структуры XML документов
- Извлечение метаданных полей
- Определение типов данных
- Статистический анализ содержимого
- Обработку вложенных структур
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Set, Optional, Tuple
from collections import defaultdict, Counter
import re
from datetime import datetime
from dataclasses import dataclass

from models.extract import Attribute, PostgreSqlDataType


@dataclass
class XMLFieldInfo:
    """Информация о поле XML."""
    
    xpath: str
    element_name: str
    data_type: PostgreSqlDataType
    sample_values: List[str]
    is_nullable: bool
    max_length: int
    is_attribute: bool = False
    parent_path: str = ""
    occurrence_count: int = 0


@dataclass
class XMLStructureAnalysis:
    """Результат анализа XML структуры."""
    
    fields: List[XMLFieldInfo]
    total_records: int
    max_depth: int
    unique_elements: int
    file_size_bytes: int
    encoding: str = "utf-8"
    root_element: str = ""
    namespace_info: Dict[str, str] = None


class XMLDataTypeDetector:
    """Детектор типов данных для XML значений."""
    
    @staticmethod
    def detect_data_type(values: List[str]) -> PostgreSqlDataType:
        """
        Определение типа данных на основе образцов значений.
        
        Args:
            values: Список значений для анализа
            
        Returns:
            Наиболее подходящий PostgreSQL тип данных
        """
        if not values:
            return PostgreSqlDataType.TEXT
        
        # Счетчики для различных типов
        type_counts = {
            'boolean': 0,
            'integer': 0,
            'numeric': 0,
            'date': 0,
            'timestamp': 0,
            'text': 0
        }
        
        for value in values:
            if not value or not value.strip():
                continue
                
            value = value.strip()
            
            # Boolean
            if value.lower() in ['true', 'false', 'yes', 'no', '1', '0']:
                type_counts['boolean'] += 1
                continue
            
            # Integer
            if re.match(r'^-?\d+$', value):
                type_counts['integer'] += 1
                continue
            
            # Numeric (float/decimal)
            if re.match(r'^-?\d+\.\d+$', value):
                type_counts['numeric'] += 1
                continue
            
            # Date patterns
            if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                type_counts['date'] += 1
                continue
                
            # Timestamp patterns
            if re.match(r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}', value):
                type_counts['timestamp'] += 1
                continue
            
            # Everything else is text
            type_counts['text'] += 1
        
        # Определяем преобладающий тип
        max_type = max(type_counts.items(), key=lambda x: x[1])[0]
        
        type_mapping = {
            'boolean': PostgreSqlDataType.BOOLEAN,
            'integer': PostgreSqlDataType.INTEGER,
            'numeric': PostgreSqlDataType.NUMERIC,
            'date': PostgreSqlDataType.DATE,
            'timestamp': PostgreSqlDataType.TIMESTAMP,
            'text': PostgreSqlDataType.TEXT
        }
        
        return type_mapping[max_type]


class XMLParser:
    """Полноценный парсер XML файлов."""
    
    def __init__(self, max_sample_values: int = 10, max_depth: int = 20):
        """
        Инициализация парсера.
        
        Args:
            max_sample_values: Максимальное количество образцов значений для анализа
            max_depth: Максимальная глубина анализа вложенности
        """
        self.max_sample_values = max_sample_values
        self.max_depth = max_depth
        self.type_detector = XMLDataTypeDetector()
    
    def analyze_xml_file(self, file_path: Path) -> XMLStructureAnalysis:
        """
        Анализ одного XML файла.
        
        Args:
            file_path: Путь к XML файлу
            
        Returns:
            Результат анализа структуры
        """
        try:
            # Парсинг XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Базовая информация
            file_size = file_path.stat().st_size
            root_name = root.tag
            
            # Сбор информации о полях
            field_info = defaultdict(lambda: {
                'values': [],
                'count': 0,
                'is_attribute': False,
                'parent_path': ''
            })
            
            # Рекурсивный обход XML структуры
            max_depth = self._analyze_element_recursive(
                root, "", field_info, 0
            )
            
            # Преобразование в XMLFieldInfo
            fields = []
            for xpath, info in field_info.items():
                if info['values']:  # Только поля с значениями
                    field = XMLFieldInfo(
                        xpath=xpath,
                        element_name=xpath.split('/')[-1],
                        data_type=self.type_detector.detect_data_type(info['values']),
                        sample_values=info['values'][:self.max_sample_values],
                        is_nullable=True,  # По умолчанию считаем nullable
                        max_length=max(len(str(v)) for v in info['values']) if info['values'] else 0,
                        is_attribute=info['is_attribute'],
                        parent_path=info['parent_path'],
                        occurrence_count=info['count']
                    )
                    fields.append(field)
            
            # Подсчет записей (примерная оценка)
            total_records = self._estimate_record_count(root)
            
            return XMLStructureAnalysis(
                fields=fields,
                total_records=total_records,
                max_depth=max_depth,
                unique_elements=len(fields),
                file_size_bytes=file_size,
                root_element=root_name
            )
            
        except Exception as e:
            print(f"Ошибка анализа XML файла {file_path}: {e}")
            return XMLStructureAnalysis(
                fields=[],
                total_records=0,
                max_depth=0,
                unique_elements=0,
                file_size_bytes=0,
                root_element="error"
            )
    
    def _analyze_element_recursive(
        self, 
        element: ET.Element, 
        current_path: str, 
        field_info: Dict, 
        depth: int
    ) -> int:
        """
        Рекурсивный анализ XML элемента.
        
        Args:
            element: XML элемент
            current_path: Текущий XPath
            field_info: Словарь для сбора информации о полях
            depth: Текущая глубина
            
        Returns:
            Максимальная достигнутая глубина
        """
        if depth > self.max_depth:
            return depth
        
        # Формируем XPath для текущего элемента
        element_path = f"{current_path}/{element.tag}" if current_path else element.tag
        max_depth_reached = depth
        
        # Анализируем атрибуты элемента
        for attr_name, attr_value in element.attrib.items():
            attr_path = f"{element_path}/@{attr_name}"
            field_info[attr_path]['values'].append(attr_value)
            field_info[attr_path]['count'] += 1
            field_info[attr_path]['is_attribute'] = True
            field_info[attr_path]['parent_path'] = element_path
        
        # Анализируем текстовое содержимое
        if element.text and element.text.strip():
            field_info[element_path]['values'].append(element.text.strip())
            field_info[element_path]['count'] += 1
            field_info[element_path]['parent_path'] = current_path
        
        # Рекурсивно анализируем дочерние элементы
        for child in element:
            child_depth = self._analyze_element_recursive(
                child, element_path, field_info, depth + 1
            )
            max_depth_reached = max(max_depth_reached, child_depth)
        
        return max_depth_reached
    
    def _estimate_record_count(self, root: ET.Element) -> int:
        """
        Оценка количества записей в XML документе.
        
        Args:
            root: Корневой элемент XML
            
        Returns:
            Приблизительное количество записей
        """
        # Ищем повторяющиеся элементы на втором уровне
        second_level_counts = Counter()
        
        for child in root:
            for grandchild in child:
                second_level_counts[grandchild.tag] += 1
        
        if second_level_counts:
            # Берем максимальное количество одинаковых элементов
            return max(second_level_counts.values())
        else:
            # Если нет вложенности, считаем дочерние элементы корня
            return len(list(root))
    
    def analyze_xml_folder(self, folder_path: Path) -> Tuple[XMLStructureAnalysis, List[str]]:
        """
        Анализ папки с XML файлами.
        
        Args:
            folder_path: Путь к папке с XML файлами
            
        Returns:
            Tuple из общего анализа и списка обработанных файлов
        """
        xml_files = list(folder_path.glob("*.xml"))
        
        if not xml_files:
            return XMLStructureAnalysis(
                fields=[], total_records=0, max_depth=0, 
                unique_elements=0, file_size_bytes=0
            ), []
        
        # Анализируем первые несколько файлов для получения схемы
        sample_files = xml_files[:min(3, len(xml_files))]
        
        combined_fields = {}
        total_records = 0
        total_size = 0
        max_depth = 0
        processed_files = []
        
        for xml_file in sample_files:
            try:
                analysis = self.analyze_xml_file(xml_file)
                total_records += analysis.total_records
                total_size += analysis.file_size_bytes
                max_depth = max(max_depth, analysis.max_depth)
                processed_files.append(xml_file.name)
                
                # Объединяем поля из разных файлов
                for field in analysis.fields:
                    if field.xpath in combined_fields:
                        # Объединяем значения и обновляем статистику
                        existing_field = combined_fields[field.xpath]
                        existing_field.sample_values.extend(field.sample_values)
                        existing_field.sample_values = existing_field.sample_values[:self.max_sample_values]
                        existing_field.occurrence_count += field.occurrence_count
                        existing_field.max_length = max(existing_field.max_length, field.max_length)
                    else:
                        combined_fields[field.xpath] = field
                        
            except Exception as e:
                print(f"Ошибка анализа файла {xml_file}: {e}")
        
        # Экстраполируем статистику на все файлы
        if sample_files:
            files_multiplier = len(xml_files) / len(sample_files)
            total_records = int(total_records * files_multiplier)
            total_size = sum(f.stat().st_size for f in xml_files)
        
        # Пересчитываем типы данных с учетом всех значений
        for field in combined_fields.values():
            if field.sample_values:
                field.data_type = self.type_detector.detect_data_type(field.sample_values)
        
        return XMLStructureAnalysis(
            fields=list(combined_fields.values()),
            total_records=total_records,
            max_depth=max_depth,
            unique_elements=len(combined_fields),
            file_size_bytes=total_size
        ), processed_files
    
    def convert_to_extract_attributes(self, analysis: XMLStructureAnalysis) -> List[Attribute]:
        """
        Преобразование результатов анализа в формат Attribute для ExtractConfig.
        
        Args:
            analysis: Результат анализа XML
            
        Returns:
            Список атрибутов в формате модели Extract
        """
        attributes = []
        
        for i, field in enumerate(analysis.fields, 1):
            attr = Attribute(
                order_no=i,
                column_name=field.xpath.replace('/', '_').replace('@', 'attr_'),
                data_type=field.data_type,
                is_nullable=field.is_nullable,
                character_maximum_length=min(field.max_length, 65535) if field.data_type in [
                    PostgreSqlDataType.TEXT, PostgreSqlDataType.VARCHAR, PostgreSqlDataType.CHARACTER_VARYING
                ] else None,
                numeric_precision=10 if field.data_type in [
                    PostgreSqlDataType.INTEGER, PostgreSqlDataType.NUMERIC, PostgreSqlDataType.DECIMAL
                ] else None,
                numeric_scale=2 if field.data_type in [
                    PostgreSqlDataType.NUMERIC, PostgreSqlDataType.DECIMAL
                ] else 0
            )
            attributes.append(attr)
        
        return attributes


# Экспорт основных классов
__all__ = [
    "XMLParser",
    "XMLStructureAnalysis", 
    "XMLFieldInfo",
    "XMLDataTypeDetector"
]