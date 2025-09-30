"""
Демонстрационный скрипт ETL DAG Generation System

Этот скрипт демонстрирует полный жизненный цикл создания ETL пайплайна:
1. Анализ XML источника данных
2. Создание конфигураций Extract/Transform/Load
3. Генерация AI рекомендаций
4. Создание Airflow DAG кода
5. Документация и развертывание

Запуск: python demo_dag_generation.py
"""

import asyncio
import sys
from pathlib import Path
import json

# Добавление пути к модулю
sys.path.append(".")

from dag_generation import (
    ETLDAGGenerationSystem,
    print_system_info,
    __version__
)


async def demo_xml_pipeline():
    """Демонстрация создания пайплайна для XML данных."""
    
    print("🎬 === ДЕМОНСТРАЦИЯ СОЗДАНИЯ XML ETL ПАЙПЛАЙНА ===\n")
    
    # Инициализация системы
    system = ETLDAGGenerationSystem(output_base_dir="demo_output")
    
    # Параметры пайплайна
    xml_source = "file://d:/lct-hack-2025/backend/parsers/sample/XML/"
    pipeline_name = "Demo Geospatial XML Processing"
    
    print(f"📂 Источник данных: {xml_source}")
    print(f"🏷️  Название пайплайна: {pipeline_name}")
    print()
    
    try:
        # Создание пайплайна
        result = await system.create_complete_etl_pipeline(
            source_url=xml_source,
            pipeline_name=pipeline_name,
            owner="demo_user",
            team="demo_team",
            generate_airflow_code=True
        )
        
        if result.get("success", True):
            # Вывод результатов
            print("\n🎉 === РЕЗУЛЬТАТЫ СОЗДАНИЯ ===")
            print(f"✅ Пайплайн ID: {result['pipeline_id']}")
            print(f"📁 Директория: {result['pipeline_directory']}")
            print(f"⏱️  Время создания: {result['duration_seconds']:.1f} сек")
            
            # AI рекомендации
            ai_recs = result.get('ai_recommendations', [])
            print(f"🤖 AI рекомендации: {len(ai_recs)}")
            
            for i, rec in enumerate(ai_recs[:3], 1):  # Показываем первые 3
                print(f"   {i}. {rec.title} (уверенность: {rec.confidence_score:.0%})")
            
            # Созданные файлы
            generated_files = result.get('generated_files', {})
            print(f"📄 Созданные файлы: {len(generated_files)}")
            
            for file_type, file_path in generated_files.items():
                file_name = Path(file_path).name
                file_size = Path(file_path).stat().st_size
                print(f"   • {file_type}: {file_name} ({file_size} байт)")
            
            # Показываем содержимое основного DAG файла (первые строки)
            if 'dag_file' in generated_files:
                dag_file_path = generated_files['dag_file']
                print(f"\n📋 Превью DAG файла ({Path(dag_file_path).name}):")
                print("=" * 60)
                
                with open(dag_file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:20]  # Первые 20 строк
                    for i, line in enumerate(lines, 1):
                        print(f"{i:2d} | {line.rstrip()}")
                
                print("...")
                print("=" * 60)
            
            # Показываем конфигурацию пайплайна
            pipeline_config = result['pipeline_config']
            print(f"\n⚙️ Конфигурация пайплайна:")
            print(f"   • Тип источника: {pipeline_config.pipeline_config.extract_config.source_type}")
            print(f"   • Формат данных: {pipeline_config.pipeline_config.extract_config.content_type}")
            print(f"   • Размер данных: {pipeline_config.pipeline_config.extract_config.source_metrics.estimated_size_mb} МБ")
            print(f"   • Количество записей: {pipeline_config.pipeline_config.extract_config.source_metrics.estimated_records:,}")
            print(f"   • Целевое хранилище: {pipeline_config.pipeline_config.load_config.target_storage_type}")
            print(f"   • Ожидаемое время: {pipeline_config.pipeline_config.estimated_runtime_minutes} мин")
            
            return result
            
        else:
            print(f"\n❌ Ошибка создания пайплайна:")
            print(f"   {result.get('error', 'Неизвестная ошибка')}")
            return None
            
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        print(f"   Тип ошибки: {type(e).__name__}")
        return None


async def demo_system_status():
    """Демонстрация получения статуса системы."""
    
    print("\n📊 === СТАТУС СИСТЕМЫ ===")
    
    system = ETLDAGGenerationSystem(output_base_dir="demo_output")
    status = await system.get_system_status()
    
    print(f"🚀 Система готова: {status['system_ready']}")
    print(f"📁 Директория вывода: {status['output_directory']}")
    print(f"🔢 Всего пайплайнов: {status['total_pipelines_created']}")
    print(f"✅ Успешных: {status['successful_pipelines']}")
    
    if status['total_pipelines_created'] > 0:
        print(f"📈 Процент успеха: {status['success_rate']:.0%}")
        print(f"🕒 Последний созданный: {status['last_created']}")


async def demo_multiple_sources():
    """Демонстрация создания пайплайнов из нескольких источников."""
    
    print("\n🔄 === СОЗДАНИЕ МНОЖЕСТВЕННЫХ ПАЙПЛАЙНОВ ===")
    
    system = ETLDAGGenerationSystem(output_base_dir="demo_output")
    
    # Определяем несколько источников для демонстрации
    sources = [
        {
            "url": "file://d:/lct-hack-2025/backend/parsers/sample/XML/",
            "name": "XML Geospatial Data"
        },
        {
            "url": "postgres://localhost:5432/demo_db",
            "name": "PostgreSQL Demo Data"
        }
    ]
    
    print(f"Создание {len(sources)} пайплайнов...")
    
    # Создание пайплайнов (только первый для демо, так как второй источник может быть недоступен)
    results = []
    
    for source in sources[:1]:  # Только XML для демонстрации
        print(f"\n🔨 Создание пайплайна: {source['name']}")
        
        try:
            result = await system.create_complete_etl_pipeline(
                source_url=source["url"],
                pipeline_name=source["name"],
                owner="multi_demo_user",
                team="batch_processing",
                generate_airflow_code=True
            )
            results.append(result)
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            results.append({"name": source["name"], "error": str(e)})
    
    # Итоги
    successful = len([r for r in results if r.get("success", True)])
    print(f"\n📊 Итого: {successful}/{len(results)} пайплайнов создано успешно")
    
    return results


def show_file_structure(demo_result):
    """Показ структуры созданных файлов."""
    
    if not demo_result or not demo_result.get("success", True):
        print("❌ Нет результатов для отображения структуры файлов")
        return
    
    print("\n📁 === СТРУКТУРА СОЗДАННЫХ ФАЙЛОВ ===")
    
    pipeline_dir = Path(demo_result["pipeline_directory"])
    
    def print_tree(path: Path, prefix: str = ""):
        """Рекурсивный вывод дерева файлов."""
        
        if not path.exists():
            return
        
        items = list(path.iterdir())
        items.sort(key=lambda x: (x.is_file(), x.name))
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item.name}")
            
            if item.is_dir() and item.name != "__pycache__":
                next_prefix = prefix + ("    " if is_last else "│   ")
                print_tree(item, next_prefix)
            elif item.is_file():
                # Показываем размер файла
                size = item.stat().st_size
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size / (1024 * 1024):.1f} MB"
                
                # Добавляем размер к имени файла
                current_line = f"{prefix}{current_prefix}{item.name}"
                padding = max(50 - len(current_line), 1)
                print(f"{current_line}{' ' * padding}({size_str})")
    
    print(f"📂 {pipeline_dir.name}/")
    print_tree(pipeline_dir)


async def main():
    """Главная функция демонстрации."""
    
    # Показываем информацию о системе
    print_system_info()
    
    print(f"\n🎯 Запуск демонстрации ETL DAG Generation System v{__version__}")
    print("=" * 70)
    
    try:
        # 1. Создание XML пайплайна
        xml_result = await demo_xml_pipeline()
        
        # 2. Показ структуры файлов
        if xml_result:
            show_file_structure(xml_result)
        
        # 3. Статус системы
        await demo_system_status()
        
        # 4. Множественные пайплайны (опционально)
        # await demo_multiple_sources()
        
        print("\n🏁 === ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА ===")
        
        if xml_result:
            print(f"✅ Пайплайн создан успешно!")
            print(f"📂 Результаты в: {xml_result['pipeline_directory']}")
            print(f"🚀 Готов к развертыванию в Airflow")
        
        print("\n💡 Следующие шаги:")
        print("   1. Изучите созданные файлы")
        print("   2. Настройте подключения к базам данных") 
        print("   3. Скопируйте DAG файлы в Airflow")
        print("   4. Запустите тестовое выполнение")
        
    except KeyboardInterrupt:
        print("\n⏹️  Демонстрация прервана пользователем")
        
    except Exception as e:
        print(f"\n💥 Критическая ошибка демонстрации: {e}")
        print(f"   Тип: {type(e).__name__}")


if __name__ == "__main__":
    asyncio.run(main())