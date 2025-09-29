"""Folder extract configuration builder."""

import sys
import os
import glob
from pathlib import Path
from typing import Dict, List, Any
import asyncio
import json
import pandas as pd
from ydata_profiling import ProfileReport

from models.extract import Content, ContentType, Source

from .base import BaseExtractConfigBuilder


class FolderExtractConfigBuilder(BaseExtractConfigBuilder):
    """Builder for folder source configurations.

    Extracts metadata from folder sources.
    """

    @classmethod
    async def get_content_metadata(cls, source: Source) -> list[Content]:
        """Extract content metadata from folder source."""
        folder_path = source.connection_string
        contents = []
        
        # Ищем файлы в папке
        supported_extensions = ['*.csv', '*.json', '*.xml']
        
        for extension in supported_extensions:
            pattern = os.path.join(folder_path, extension)
            for file_path in glob.glob(pattern):
                file_name = os.path.basename(file_path)
                
                # Для CSV файлов используем ваш анализатор
                if file_path.endswith('.csv'):
                    analysis_result = await cls._analyze_csv_file(file_path)
                    metamodel = {
                        'file_type': 'csv',
                        'analysis': analysis_result,
                        'file_name': file_name
                    }
                # Для JSON и XML - заглушки
                elif file_path.endswith('.json'):
                    metamodel = {
                        'file_type': 'json',
                        'status': 'not_implemented',
                        'file_name': file_name,
                        'file_size': os.path.getsize(file_path)
                    }
                elif file_path.endswith('.xml'):
                    metamodel = {
                        'file_type': 'xml', 
                        'status': 'not_implemented',
                        'file_name': file_name,
                        'file_size': os.path.getsize(file_path)
                    }
                
                content = Content(
                    message_name=file_name,
                    metamodel=metamodel
                )
                contents.append(content)
        
        return contents

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
        """Retrieve statistics about the source content.

        Args:
            source: The source configuration.

        Returns:
            Dictionary containing content statistics with
            any additional information about the source.
        """
        folder_path = source.connection_string
        
        try:
            # Ищем CSV файлы в папке
            csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
            
            if not csv_files:
                return {"error": "No CSV files found in folder"}
            
            # Анализируем первый CSV файл (или можно проанализировать все и объединить)
            first_csv_file = csv_files[0]
            analysis_result = await cls._analyze_csv_file(first_csv_file)
            
            # Возвращаем variables_data как основную статистику
            statistics = {
                'file_analyzed': os.path.basename(first_csv_file),
                'variables_statistics': analysis_result.get('variables', {}),
                'table_summary': analysis_result.get('table', {}),
                'columns': analysis_result.get('columns', []),
                'row_count': analysis_result.get('row_count', 0),
                'total_csv_files': len(csv_files)
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
        """Analyze CSV file (placeholder for future implementation)."""
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

            # Возвращаем variables_data как основную статистику
            variables_data = cleaned_data.get('variables', {})
            
            return {
                'variables': variables_data,
                'table': data.get('table', {}),
                'columns': list(df.columns),
                'row_count': len(df),
                'file_size': os.path.getsize(file_path),
                'file_name': os.path.basename(file_path)
            }
            
        except Exception as e:
            return {'error': str(e)}