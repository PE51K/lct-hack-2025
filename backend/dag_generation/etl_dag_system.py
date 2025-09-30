"""
ETL DAG Generation System - Main Interface

Основной интерфейс для создания полных ETL пайплайнов из источников данных.
Объединяет все компоненты системы:

1. 📊 Анализ источников данных
2. ⚙️ Создание конфигураций Extract/Transform/Load  
3. 🤖 AI рекомендации по оптимизации
4. 🏗️ Генерация Airflow DAG кода
5. 📋 Документация и развертывание

Использование:
    dag_system = ETLDAGGenerationSystem()
    result = await dag_system.create_complete_etl_pipeline(source_url, pipeline_name)
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

sys.path.append("..")

from .comprehensive_dag_builder import ComprehensiveDAGBuilder
from .enhanced_airflow_generator import EnhancedAirflowDAGGenerator
from .pipeline_config_models import CompletePipelineWithAI


class ETLDAGGenerationSystem:
    """
    Полная система генерации ETL DAG пайплайнов.
    
    Основной класс, объединяющий все компоненты системы для создания
    готовых к развертыванию Airflow DAG из источников данных.
    """
    
    def __init__(self, output_base_dir: str = "generated_etl_pipelines"):
        """
        Инициализация системы генерации DAG.
        
        Args:
            output_base_dir: Базовая директория для всех создаваемых файлов
        """
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(exist_ok=True)
        
        # Инициализация компонентов
        self.dag_builder = ComprehensiveDAGBuilder()
        self.airflow_generator = None  # Инициализируется в create_pipeline
        
        # Отчет о созданных пайплайнах
        self.creation_report = {
            "created_pipelines": [],
            "total_pipelines": 0,
            "last_created": None
        }
    
    async def create_complete_etl_pipeline(
        self,
        source_url: str,
        pipeline_name: str,
        owner: str = "data_team",
        team: str = "analytics",
        generate_airflow_code: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Создание полного ETL пайплайна из источника данных.
        
        Args:
            source_url: URL или путь к источнику данных
            pipeline_name: Название пайплайна
            owner: Владелец пайплайна
            team: Команда
            generate_airflow_code: Генерировать ли Airflow код
            **kwargs: Дополнительные параметры конфигурации
            
        Returns:
            Результат создания пайплайна с путями к файлам
        """
        
        start_time = datetime.now()
        pipeline_id = f"etl_{pipeline_name.lower().replace(' ', '_').replace('-', '_')}"
        
        print(f"🚀 === СОЗДАНИЕ ETL ПАЙПЛАЙНА ===")
        print(f"📋 Название: {pipeline_name}")
        print(f"🆔 ID: {pipeline_id}")
        print(f"📂 Источник: {source_url}")
        print(f"👤 Владелец: {owner}")
        print(f"🏢 Команда: {team}")
        print(f"⏰ Начало: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        try:
            # === ШАГ 1: СОЗДАНИЕ КОНФИГУРАЦИИ ПАЙПЛАЙНА ===
            print("\\n📊 ШАГ 1: Анализ источника и создание конфигурации...")
            
            pipeline_config = await self.dag_builder.build_complete_pipeline_from_url(
                source_url=source_url,
                pipeline_name=pipeline_name,
                owner=owner,
                team=team
            )
            
            print(f"✅ Конфигурация создана успешно!")
            print(f"   🔗 Источник: {pipeline_config.pipeline_config.extract_config.source_type}")
            print(f"   📄 Формат: {pipeline_config.pipeline_config.extract_config.content_type}")
            print(f"   🏪 Хранилище: {pipeline_config.pipeline_config.load_config.target_storage_type}")
            print(f"   🤖 AI рекомендации: {len(pipeline_config.ai_recommendations)}")
            
            # === ШАГ 2: СОХРАНЕНИЕ КОНФИГУРАЦИИ ===
            print("\\n💾 ШАГ 2: Сохранение конфигурации пайплайна...")
            
            # Создание директории для пайплайна
            pipeline_dir = self.output_base_dir / pipeline_id
            pipeline_dir.mkdir(exist_ok=True)
            
            # Сохранение JSON конфигурации
            config_saved = await self.dag_builder.save_pipeline_config(
                pipeline_config, 
                str(pipeline_dir)
            )
            
            result = {
                "pipeline_id": pipeline_id,
                "pipeline_name": pipeline_name,
                "pipeline_config": pipeline_config,
                "config_file": config_saved,
                "pipeline_directory": str(pipeline_dir),
                "generated_files": {},
                "creation_time": start_time,
                "ai_recommendations": pipeline_config.ai_recommendations
            }
            
            # === ШАГ 3: ГЕНЕРАЦИЯ AIRFLOW КОДА ===
            if generate_airflow_code:
                print("\\n🏗️ ШАГ 3: Генерация Airflow DAG кода...")
                
                # Создание Airflow генератора с директорией пайплайна
                self.airflow_generator = EnhancedAirflowDAGGenerator(str(pipeline_dir / "airflow"))
                
                # Генерация всех файлов Airflow
                airflow_files = await self.airflow_generator.generate_complete_dag(pipeline_config)
                
                result["generated_files"] = airflow_files
                
                print(f"✅ Airflow DAG сгенерирован!")
                print("   📁 Созданные файлы:")
                for file_type, file_path in airflow_files.items():
                    print(f"      {file_type}: {Path(file_path).name}")
            
            # === ШАГ 4: СОЗДАНИЕ ОТЧЕТА ===
            print("\\n📋 ШАГ 4: Создание отчета о пайплайне...")
            
            report = await self._create_pipeline_report(pipeline_config, result)
            report_file = pipeline_dir / f"{pipeline_id}_report.md"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            result["report_file"] = str(report_file)
            
            # === ЗАВЕРШЕНИЕ ===
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result["completion_time"] = end_time
            result["duration_seconds"] = duration
            
            # Обновление отчета системы
            self._update_system_report(result)
            
            print("\\n🎉 === СОЗДАНИЕ ЗАВЕРШЕНО УСПЕШНО ===")
            print(f"⏱️ Время выполнения: {duration:.1f} секунд")
            print(f"📁 Директория: {pipeline_dir}")
            print(f"📊 Оценка времени работы: {pipeline_config.pipeline_config.estimated_runtime_minutes} мин")
            print(f"💾 Конфигурация: {Path(config_saved).name}")
            
            if generate_airflow_code:
                print(f"🚀 Готов к развертыванию в Airflow!")
            
            return result
            
        except Exception as e:
            error_time = datetime.now()
            duration = (error_time - start_time).total_seconds()
            
            print(f"\\n❌ === ОШИБКА СОЗДАНИЯ ПАЙПЛАЙНА ===")
            print(f"⏱️ Время до ошибки: {duration:.1f} секунд")
            print(f"🚨 Ошибка: {str(e)}")
            print(f"📍 Тип: {type(e).__name__}")
            
            # Возвращаем информацию об ошибке
            return {
                "pipeline_id": pipeline_id,
                "pipeline_name": pipeline_name,
                "error": str(e),
                "error_type": type(e).__name__,
                "creation_time": start_time,
                "error_time": error_time,
                "duration_seconds": duration,
                "success": False
            }
    
    async def create_multiple_pipelines(
        self,
        sources: List[Dict[str, str]],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Создание множества пайплайнов из списка источников.
        
        Args:
            sources: Список источников в формате [{"url": "...", "name": "..."}, ...]
            **kwargs: Дополнительные параметры для всех пайплайнов
            
        Returns:
            Список результатов создания пайплайнов
        """
        
        print(f"🔄 Создание {len(sources)} ETL пайплайнов...")
        
        results = []
        
        for i, source in enumerate(sources, 1):
            print(f"\\n--- Пайплайн {i}/{len(sources)} ---")
            
            try:
                result = await self.create_complete_etl_pipeline(
                    source_url=source["url"],
                    pipeline_name=source["name"],
                    **kwargs
                )
                results.append(result)
                
            except Exception as e:
                print(f"❌ Ошибка создания пайплайна '{source['name']}': {e}")
                results.append({
                    "pipeline_name": source["name"],
                    "source_url": source["url"],
                    "error": str(e),
                    "success": False
                })
        
        successful = len([r for r in results if r.get("success", True)])
        print(f"\\n📊 Итого: {successful}/{len(sources)} пайплайнов создано успешно")
        
        return results
    
    async def _create_pipeline_report(
        self, 
        pipeline_config: CompletePipelineWithAI, 
        creation_result: Dict[str, Any]
    ) -> str:
        """Создание подробного отчета о пайплайне."""
        
        config = pipeline_config.pipeline_config
        
        # Базовая информация
        report_lines = [
            f"# Отчет ETL Пайплайна: {config.metadata.pipeline_name}",
            "",
            f"**Создан:** {creation_result['creation_time'].strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Pipeline ID:** `{config.metadata.pipeline_id}`",
            f"**Владелец:** {config.metadata.owner}",
            f"**Команда:** {config.metadata.team}",
            f"**Критичность:** {config.metadata.criticality}",
            "",
            "## 📊 Характеристики данных",
            "",
            f"- **Тип источника:** {config.extract_config.source_type}",
            f"- **Формат данных:** {config.extract_config.content_type}",
            f"- **Размер данных:** {config.extract_config.source_metrics.estimated_size_mb} МБ",
            f"- **Количество записей:** {config.extract_config.source_metrics.estimated_records:,}",
            f"- **Сложность:** {config.extract_config.source_metrics.complexity_score}/10",
            f"- **Уровни вложенности:** {config.extract_config.source_metrics.nested_levels}",
            "",
            "## ⚙️ Конфигурация обработки",
            "",
            f"- **Размер батча:** {config.extract_config.batch_size}",
            f"- **Параллельные воркеры:** {config.extract_config.resources.parallel_workers}",
            f"- **Ожидаемое время:** {config.estimated_runtime_minutes} минут",
            f"- **Требования CPU:** {config.total_cpu_cores} ядер",
            f"- **Требования RAM:** {config.total_memory_mb} МБ",
            "",
            "## 🏪 Целевое хранилище",
            "",
            f"- **Тип хранилища:** {config.load_config.target_storage_type}",
            f"- **База данных:** {config.load_config.database_name}",
            f"- **Схема:** {config.load_config.schema_name}",
            f"- **Таблица:** {config.load_config.table_name}",
            f"- **Стратегия загрузки:** {config.load_config.load_strategy}",
            ""
        ]
        
        # AI рекомендации
        if pipeline_config.ai_recommendations:
            report_lines.extend([
                "## 🤖 AI Рекомендации",
                ""
            ])
            
            for i, rec in enumerate(pipeline_config.ai_recommendations, 1):
                report_lines.extend([
                    f"### {i}. {rec.title}",
                    f"**Тип:** {rec.recommendation_type}",
                    f"**Описание:** {rec.description}",
                    f"**Уверенность:** {rec.confidence_score:.0%}",
                    f"**Воздействие:** {rec.impact_level}",
                    ""
                ])
                
                if rec.estimated_improvement:
                    report_lines.append("**Ожидаемые улучшения:**")
                    for metric, improvement in rec.estimated_improvement.items():
                        report_lines.append(f"- {metric}: {improvement:.1f}x")
                    report_lines.append("")
                
                if rec.implementation_steps:
                    report_lines.extend(["**Шаги внедрения:**"])
                    for step in rec.implementation_steps:
                        report_lines.append(f"- {step}")
                    report_lines.append("")
        
        # Метрики производительности
        if pipeline_config.baseline_metrics:
            baseline = pipeline_config.baseline_metrics
            target = pipeline_config.target_metrics
            
            report_lines.extend([
                "## 📈 Метрики производительности",
                "",
                "| Метрика | Базовая | Целевая | Улучшение |",
                "|---------|---------|---------|-----------|"
            ])
            
            metrics = [
                ("Пропускная способность (зап/мин)", "throughput_records_per_minute", ""),
                ("Задержка (мин)", "latency_minutes", ""),
                ("Утилизация CPU", "resource_utilization_cpu", "%"),
                ("Утилизация RAM", "resource_utilization_memory", "%"),
                ("Стоимость выполнения ($)", "cost_per_execution_usd", ""),
                ("Качество данных", "data_quality_score", "%"),
                ("Надежность", "reliability_score", "%")
            ]
            
            for name, attr, suffix in metrics:
                base_val = getattr(baseline, attr)
                target_val = getattr(target, attr) if target else base_val
                
                if attr in ["resource_utilization_cpu", "resource_utilization_memory", "data_quality_score", "reliability_score"]:
                    base_str = f"{base_val:.1%}"
                    target_str = f"{target_val:.1%}"
                else:
                    base_str = f"{base_val:.1f}{suffix}"
                    target_str = f"{target_val:.1f}{suffix}"
                
                improvement = ((target_val - base_val) / base_val * 100) if base_val != 0 else 0
                improvement_str = f"{improvement:+.1f}%" if improvement != 0 else "—"
                
                report_lines.append(f"| {name} | {base_str} | {target_str} | {improvement_str} |")
            
            report_lines.append("")
        
        # Созданные файлы
        report_lines.extend([
            "## 📁 Созданные файлы",
            ""
        ])
        
        if creation_result.get("generated_files"):
            report_lines.append("### Airflow DAG файлы:")
            for file_type, file_path in creation_result["generated_files"].items():
                file_name = Path(file_path).name
                report_lines.append(f"- **{file_type}**: `{file_name}`")
            report_lines.append("")
        
        report_lines.extend([
            f"- **Конфигурация**: `{Path(creation_result['config_file']).name}`",
            f"- **Отчет**: `{config.metadata.pipeline_id}_report.md`",
            ""
        ])
        
        # Следующие шаги
        report_lines.extend([
            "## 🚀 Следующие шаги",
            "",
            "1. **Проверка конфигурации** - Проверьте настройки подключений",
            "2. **Создание целевых таблиц** - Выполните DDL скрипты",
            "3. **Развертывание в Airflow** - Скопируйте DAG файлы",
            "4. **Тестирование** - Выполните тестовый запуск",
            "5. **Мониторинг** - Настройте алерты и дашборды",
            "",
            "---",
            f"*Отчет создан автоматически {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])
        
        return "\\n".join(report_lines)
    
    def _update_system_report(self, pipeline_result: Dict[str, Any]):
        """Обновление системного отчета о созданных пайплайнах."""
        
        self.creation_report["created_pipelines"].append({
            "pipeline_id": pipeline_result["pipeline_id"],
            "pipeline_name": pipeline_result["pipeline_name"],
            "creation_time": pipeline_result["creation_time"],
            "success": pipeline_result.get("success", True),
            "duration_seconds": pipeline_result.get("duration_seconds", 0)
        })
        
        self.creation_report["total_pipelines"] += 1
        self.creation_report["last_created"] = pipeline_result["creation_time"]
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса системы генерации DAG."""
        
        total_pipelines = len(self.creation_report["created_pipelines"])
        successful_pipelines = len([
            p for p in self.creation_report["created_pipelines"] 
            if p.get("success", True)
        ])
        
        return {
            "total_pipelines_created": total_pipelines,
            "successful_pipelines": successful_pipelines,
            "success_rate": successful_pipelines / total_pipelines if total_pipelines > 0 else 0,
            "last_created": self.creation_report["last_created"],
            "output_directory": str(self.output_base_dir),
            "system_ready": True
        }
    
    async def cleanup_old_pipelines(self, days_old: int = 30):
        """Очистка старых пайплайнов."""
        
        print(f"🧹 Очистка пайплайнов старше {days_old} дней...")
        
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        cleaned_count = 0
        
        for pipeline_info in self.creation_report["created_pipelines"]:
            if pipeline_info["creation_time"] < cutoff_date:
                pipeline_dir = self.output_base_dir / pipeline_info["pipeline_id"]
                
                if pipeline_dir.exists():
                    import shutil
                    shutil.rmtree(pipeline_dir)
                    cleaned_count += 1
                    print(f"   Удален: {pipeline_info['pipeline_name']}")
        
        print(f"✅ Очищено {cleaned_count} старых пайплайнов")
        return cleaned_count


# Примеры использования
async def example_single_pipeline():
    """Пример создания одного пайплайна."""
    
    system = ETLDAGGenerationSystem()
    
    result = await system.create_complete_etl_pipeline(
        source_url="file://d:/lct-hack-2025/backend/parsers/sample/XML/",
        pipeline_name="Geospatial Data Processing",
        owner="geo_data_engineer",
        team="geospatial_analytics",
        generate_airflow_code=True
    )
    
    if result.get("success", True):
        print(f"\\n🎉 Пайплайн создан: {result['pipeline_id']}")
        return result
    else:
        print(f"\\n❌ Ошибка: {result['error']}")
        return None


async def example_multiple_pipelines():
    """Пример создания нескольких пайплайнов."""
    
    system = ETLDAGGenerationSystem()
    
    sources = [
        {
            "url": "file://d:/lct-hack-2025/backend/parsers/sample/XML/",
            "name": "XML Geospatial Pipeline"
        },
        {
            "url": "postgres://localhost:5432/source_db",
            "name": "PostgreSQL Extract Pipeline"  
        }
    ]
    
    results = await system.create_multiple_pipelines(
        sources=sources,
        owner="data_engineering_team",
        team="analytics"
    )
    
    return results


async def main():
    """Демонстрация работы системы."""
    
    print("🚀 === ДЕМОНСТРАЦИЯ ETL DAG GENERATION SYSTEM ===\\n")
    
    # Создание одного пайплайна
    result = await example_single_pipeline()
    
    if result:
        # Получение статуса системы
        system = ETLDAGGenerationSystem()
        status = await system.get_system_status()
        
        print("\\n📊 === СТАТУС СИСТЕМЫ ===")
        print(f"Всего пайплайнов: {status['total_pipelines_created']}")
        print(f"Успешных: {status['successful_pipelines']}")
        print(f"Процент успеха: {status['success_rate']:.0%}")
        print(f"Директория: {status['output_directory']}")
        
        return result


if __name__ == "__main__":
    asyncio.run(main())