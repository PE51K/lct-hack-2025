"""
Интегрированный DAG Generator для основного приложения.

Этот модуль предоставляет простой интерфейс для создания ETL DAG
из основного приложения LCT-hack-2025.
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Добавляем путь к dag_generation модулю
sys.path.append(str(Path(__file__).parent.parent))

from dag_generation import ETLDAGGenerationSystem
from models.extract import ExtractConfig
from models.transform import TransformConfig  
from models.load import LoadConfig


class IntegratedDAGGenerator:
    """
    Интегрированный генератор DAG для основного приложения.
    
    Предоставляет простой интерфейс для создания ETL пайплайнов
    используя существующие builders и модели проекта.
    """
    
    def __init__(self, output_dir: str = "generated_dags"):
        """
        Инициализация генератора.
        
        Args:
            output_dir: Директория для сохранения сгенерированных DAG
        """
        self.dag_system = ETLDAGGenerationSystem(output_base_dir=output_dir)
        self.output_dir = Path(output_dir)
        
    async def create_dag_from_url(
        self,
        source_url: str,
        pipeline_name: str,
        owner: str = "data_team",
        team: str = "analytics",
        description: str = "Generated ETL pipeline"
    ) -> Dict[str, Any]:
        """
        Создание DAG из URL источника данных.
        
        Args:
            source_url: URL или путь к источнику данных
            pipeline_name: Название пайплайна
            owner: Владелец пайплайна
            team: Команда
            description: Описание пайплайна
            
        Returns:
            Результат создания DAG с метаданными
        """
        try:
            print(f"🚀 Создание DAG: {pipeline_name}")
            print(f"📂 Источник: {source_url}")
            
            # Создаем полный пайплайн
            result = await self.dag_system.create_complete_etl_pipeline(
                source_url=source_url,
                pipeline_name=pipeline_name,
                owner=owner,
                team=team,
                description=description
            )
            
            if result["success"]:
                print(f"✅ DAG успешно создан!")
                print(f"📁 Файлы сохранены в: {result['output_directory']}")
                return {
                    "success": True,
                    "pipeline_id": result["pipeline_id"],
                    "output_directory": result["output_directory"],
                    "dag_file": result["files"]["dag_file"],
                    "config_file": result["files"]["config_file"],
                    "ai_recommendations_count": len(result.get("ai_recommendations", [])),
                    "estimated_runtime_minutes": result.get("estimated_runtime_minutes", 0),
                    "message": f"DAG '{pipeline_name}' успешно создан"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Неизвестная ошибка"),
                    "message": "Ошибка создания DAG"
                }
                
        except Exception as e:
            print(f"❌ Ошибка создания DAG: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Критическая ошибка при создании DAG"
            }
    
    async def create_dag_from_configs(
        self,
        extract_config: ExtractConfig,
        transform_config: Optional[TransformConfig] = None,
        load_config: Optional[LoadConfig] = None,
        pipeline_name: str = "Custom Pipeline",
        owner: str = "data_team"
    ) -> Dict[str, Any]:
        """
        Создание DAG из готовых конфигов Extract/Transform/Load.
        
        Args:
            extract_config: Конфигурация извлечения данных
            transform_config: Конфигурация трансформации (опционально)
            load_config: Конфигурация загрузки (опционально)
            pipeline_name: Название пайплайна
            owner: Владелец пайплайна
            
        Returns:
            Результат создания DAG
        """
        try:
            print(f"🔧 Создание DAG из готовых конфигов: {pipeline_name}")
            
            # Для этого метода нужно будет расширить DAG систему
            # Пока используем URL из extract_config
            if extract_config.source_metadata and extract_config.source_metadata.connection_string:
                source_url = f"{extract_config.source_metadata.source_type}:{extract_config.source_metadata.connection_string}"
                return await self.create_dag_from_url(
                    source_url=source_url,
                    pipeline_name=pipeline_name,
                    owner=owner
                )
            else:
                return {
                    "success": False,
                    "error": "Не удается определить источник данных из ExtractConfig",
                    "message": "Некорректная конфигурация извлечения"
                }
                
        except Exception as e:
            print(f"❌ Ошибка создания DAG из конфигов: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Ошибка при создании DAG из конфигураций"
            }
    
    async def list_generated_dags(self) -> Dict[str, Any]:
        """
        Получение списка всех сгенерированных DAG.
        
        Returns:
            Список сгенерированных пайплайнов
        """
        try:
            status = await self.dag_system.get_system_status()
            
            dags = []
            if self.output_dir.exists():
                for dag_dir in self.output_dir.iterdir():
                    if dag_dir.is_dir() and not dag_dir.name.startswith('.'):
                        dag_info = {
                            "pipeline_id": dag_dir.name,
                            "created": dag_dir.stat().st_ctime,
                            "path": str(dag_dir),
                            "has_dag_file": (dag_dir / "airflow" / f"{dag_dir.name}.py").exists(),
                            "has_config": (dag_dir / f"{dag_dir.name}_config.json").exists()
                        }
                        dags.append(dag_info)
            
            return {
                "success": True,
                "total_dags": len(dags),
                "dags": dags,
                "system_status": status
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "dags": []
            }
    
    def get_supported_sources(self) -> Dict[str, Any]:
        """
        Получение списка поддерживаемых типов источников данных.
        
        Returns:
            Информация о поддерживаемых источниках
        """
        return {
            "source_types": [
                {
                    "type": "folder",
                    "name": "Локальные папки",
                    "description": "XML, JSON, CSV файлы в папках",
                    "example_url": "file://d:/data/xml_files/",
                    "supported_formats": ["xml", "json", "csv"],
                    "ready": True
                },
                {
                    "type": "postgres", 
                    "name": "PostgreSQL",
                    "description": "PostgreSQL базы данных",
                    "example_url": "postgres://user:pass@localhost:5432/mydb",
                    "supported_formats": ["table"],
                    "ready": True
                },
                {
                    "type": "clickhouse",
                    "name": "ClickHouse",
                    "description": "ClickHouse аналитические БД",
                    "example_url": "clickhouse://user:pass@localhost:8123/analytics",
                    "supported_formats": ["table"],
                    "ready": False
                },
                {
                    "type": "kafka",
                    "name": "Apache Kafka",
                    "description": "Потоковые данные из Kafka",
                    "example_url": "kafka://broker:9092/topic",
                    "supported_formats": ["json"],
                    "ready": False
                },
                {
                    "type": "s3",
                    "name": "Amazon S3",
                    "description": "Объектное хранилище S3",
                    "example_url": "s3://bucket/path/",
                    "supported_formats": ["xml", "json", "csv", "parquet"],
                    "ready": False
                },
                {
                    "type": "api",
                    "name": "REST API",
                    "description": "HTTP API эндпоинты",
                    "example_url": "https://api.example.com/data",
                    "supported_formats": ["json"],
                    "ready": False
                }
            ],
            "ready_builders": ["folder", "postgres"],
            "development_builders": ["clickhouse", "kafka", "s3", "api"]
        }


# Синхронные обертки для удобства использования
class DAGGeneratorSync:
    """Синхронная обертка для IntegratedDAGGenerator."""
    
    def __init__(self, output_dir: str = "generated_dags"):
        self.generator = IntegratedDAGGenerator(output_dir)
    
    def create_dag(self, source_url: str, pipeline_name: str, **kwargs) -> Dict[str, Any]:
        """Синхронное создание DAG."""
        return asyncio.run(self.generator.create_dag_from_url(
            source_url, pipeline_name, **kwargs
        ))
    
    def list_dags(self) -> Dict[str, Any]:
        """Синхронное получение списка DAG."""
        return asyncio.run(self.generator.list_generated_dags())


# Экспорт для использования в приложении
__all__ = [
    "IntegratedDAGGenerator",
    "DAGGeneratorSync"
]