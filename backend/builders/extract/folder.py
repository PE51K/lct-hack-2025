"""Folder extract configuration builder."""

import os
import glob
from pathlib import Path
from typing import Dict, Any
import json
import pandas as pd
from ydata_profiling import ProfileReport

from models.extract import Content, ContentType, Source

from .base import BaseExtractConfigBuilder
from .csv import clean_profile_data


class FolderExtractConfigBuilder(BaseExtractConfigBuilder):
    """Builder for folder source configurations.

    Extracts metadata from folder sources.
    """

    @classmethod
    async def get_content_metadata(cls, source: Source) -> list[Content]:
        """Extract content metadata from folder source."""
        folder_path = source.connection_string
        contents = []
        
        supported_extensions = ['*.csv', '*.json', '*.xml']
        
        for extension in supported_extensions:
            pattern = os.path.join(folder_path, extension)
            for file_path in glob.glob(pattern):
                file_name = os.path.basename(file_path)
                
                if file_path.endswith('.csv'):
                    analysis_result = await cls._analyze_csv_file(file_path)
                    metamodel = cls._convert_analysis_to_metamodel(analysis_result, file_name)
                elif file_path.endswith('.json') or file_path.endswith('.xml'):
                    metamodel = {
                        'type': 'object',
                        'properties': {},
                        'required': []
                    }
                
                content = Content(
                    message_name=file_name,
                    metamodel=metamodel
                )
                contents.append(content)
        
        return contents


    @classmethod
    def _convert_analysis_to_metamodel(cls, analysis_result: Dict[str, Any], file_name: str) -> Dict[str, Any]:
        """Convert analysis result to JSON Schema metamodel."""
        if 'error' in analysis_result:
            return {
                'type': 'object',
                'properties': {},
                'required': []
            }
        
        properties = {}
        required = []
        
        # Используем информацию о колонках для создания свойств
        columns = analysis_result.get('columns', [])
        variables_data = analysis_result.get('variables', {})
        
        for column in columns:
            if column in variables_data:
                var_info = variables_data[column]
                # Определяем тип на основе анализа
                inferred_type = cls._infer_json_schema_type(var_info, column)
                properties[column] = {'type': inferred_type}
                # Все поля считаем обязательными для простоты
                required.append(column)
            else:
                # Если нет детальной информации, используем string как fallback
                properties[column] = {'type': 'string'}
                required.append(column)
        
        return {
            'type': 'object',
            'properties': properties,
            'required': required
        }

    @classmethod
    def _infer_json_schema_type(cls, var_info: Dict[str, Any], column_name: str) -> str:
        """Infer JSON Schema type from variable analysis with improved logic."""
        # Анализируем тип из переменных
        var_type = var_info.get('type', '').lower()
        
        # Улучшенная логика определения типов
        if var_type in ['integer', 'int']:
            return 'integer'
        elif var_type in ['float', 'numeric', 'number']:
            return 'number'
        elif var_type == 'boolean' or var_type == 'bool':
            return 'boolean'
        else:
            # Эвристика на основе имени колонки
            if column_name.lower() in ['age', 'year', 'id']:
                return 'integer'
            else:
                return 'string'

    @classmethod
    async def get_src_content_type(cls, source: Source) -> ContentType:
        """Get content type for folder source."""
        # Для папки определяем тип по содержимому
        folder_path = source.connection_string
        
        try:
            files = os.listdir(folder_path)
            # Проверяем, какие файлы есть в папке
            if any(f.endswith('.csv') for f in files):
                return ContentType.csv
            elif any(f.endswith('.json') for f in files):
                return ContentType.json
            elif any(f.endswith('.xml') for f in files):
                return ContentType.xml
            else:
                return ContentType.na
        except Exception:
            return ContentType.na

    @classmethod
    async def get_content_statistics(cls, source: Source) -> dict:
        """Retrieve statistics about the source content."""
        folder_path = source.connection_string
        
        try:
            # Ищем CSV файлы в папке
            csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
            
            if not csv_files:
                return {"error": "No CSV files found in folder"}
            
            # Анализируем первый CSV файл
            first_csv_file = csv_files[0]
            analysis_result = await cls._analyze_csv_file(first_csv_file)
            
            if 'error' in analysis_result:
                return {
                    "error": analysis_result['error'],
                    "folder_path": folder_path,
                    "status": "analysis_failed"
                }
            
            # Создаем статистику в ожидаемом формате
            statistics = {
                'file_analyzed': os.path.basename(first_csv_file),
                'total_files': len(csv_files),
                'file_types': ['csv'],
                'analysis_summary': {
                    'row_count': analysis_result.get('row_count', 0),
                    'column_count': len(analysis_result.get('columns', [])),
                    'file_size': analysis_result.get('file_size', 0)
                }
            }
            
            return statistics
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error getting statistics for {folder_path}: {e}")
            return {
                "error": str(e),
                "folder_path": folder_path,
                "status": "analysis_failed"
            }

    @classmethod
    async def _analyze_csv_file(cls, file_path: Path) -> Dict[str, Any]:
        """Analyze CSV file with improved type detection."""
        try:
            SAMPLE_SIZE = 10000
            separators = [',', ';', '\t', '|']

            for sep in separators:
                try:
                    df = pd.read_csv(file_path, sep=sep, on_bad_lines='skip', 
                                engine='python', nrows=SAMPLE_SIZE)
                    if df.shape[1] > 1:
                        break
                except Exception:
                    continue
            else:
                sep = ','
                df = pd.read_csv(file_path, sep=sep, on_bad_lines='skip', 
                            engine='python', nrows=SAMPLE_SIZE)

            # Создание профиля
            profile = ProfileReport(df, title="Profiling Report", explorative=True)
            profile_json = profile.to_json()
            data = json.loads(profile_json)
            cleaned_data = clean_profile_data(data)

            return {
                'variables': cleaned_data.get('variables', {}),
                'table': data.get('table', {}),
                'columns': list(df.columns),
                'row_count': len(df),
                'file_size': os.path.getsize(file_path),
                'file_name': os.path.basename(file_path)
            }
            
        except Exception as e:
            print(f"Error analyzing CSV file {file_path}: {e}")
            return {'error': str(e)}