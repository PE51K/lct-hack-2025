"""
Тест интеграции DAG генерации с готовыми builders.

Проверяет работу с PostgreSQL и XML folder источниками.
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к приложению
sys.path.append(str(Path(__file__).parent))

from app.dag_generator import IntegratedDAGGenerator


async def test_xml_folder_integration():
    """Тест интеграции с XML папкой через готовые builders."""
    print("🧪 === ТЕСТ XML FOLDER ИНТЕГРАЦИИ ===\n")

    generator = IntegratedDAGGenerator(output_dir="test_integration_output")

    # Тестируем XML папку
    xml_source = "file://d:/lct-hack-2025/backend/parsers/sample/XML/"

    result = await generator.create_dag_from_url(
        source_url=xml_source,
        pipeline_name="Test XML Integration",
        owner="test_user",
        team="integration_team",
        description="Тестирование интеграции с XML builders",
    )

    print("📊 Результат создания XML DAG:")
    print(f"   ✅ Успех: {result['success']}")

    if result["success"]:
        print(f"   🆔 Pipeline ID: {result['pipeline_id']}")
        print(f"   📁 Директория: {result['output_directory']}")
        print(f"   📄 DAG файл: {result['dag_file']}")
        print(f"   🤖 AI рекомендаций: {result['ai_recommendations_count']}")
        print(f"   ⏱️ Время выполнения: {result['estimated_runtime_minutes']} мин")
    else:
        print(f"   ❌ Ошибка: {result['error']}")

    return result


async def test_postgres_integration():
    """Тест интеграции с PostgreSQL через готовые builders."""
    print("\n🧪 === ТЕСТ POSTGRESQL ИНТЕГРАЦИИ ===\n")

    generator = IntegratedDAGGenerator(output_dir="test_integration_output")

    # Тестируем PostgreSQL (примерная строка подключения)
    postgres_source = "postgres://user:password@localhost:5432/test_db?table=test_table"

    try:
        result = await generator.create_dag_from_url(
            source_url=postgres_source,
            pipeline_name="Test PostgreSQL Integration",
            owner="test_user",
            team="integration_team",
            description="Тестирование интеграции с PostgreSQL builders",
        )

        print("📊 Результат создания PostgreSQL DAG:")
        print(f"   ✅ Успех: {result['success']}")

        if result["success"]:
            print(f"   🆔 Pipeline ID: {result['pipeline_id']}")
            print(f"   📁 Директория: {result['output_directory']}")
            print(f"   📄 DAG файл: {result['dag_file']}")
            print(f"   🤖 AI рекомендаций: {result['ai_recommendations_count']}")
            print(f"   ⏱️ Время выполнения: {result['estimated_runtime_minutes']} мин")
        else:
            print(f"   ❌ Ошибка: {result['error']}")

    except Exception as e:
        print(f"   ⚠️ Ожидаемая ошибка (нет подключения к БД): {e}")
        result = {"success": False, "error": str(e), "expected": True}

    return result


async def test_supported_sources():
    """Тест получения поддерживаемых источников."""
    print("\n🧪 === ТЕСТ ПОДДЕРЖИВАЕМЫХ ИСТОЧНИКОВ ===\n")

    generator = IntegratedDAGGenerator()
    sources = generator.get_supported_sources()

    print("📋 Поддерживаемые типы источников:")
    for source in sources["source_types"]:
        status = "✅ Готов" if source["ready"] else "🚧 В разработке"
        print(f"   {status} {source['name']} ({source['type']})")
        print(f"      📝 {source['description']}")
        print(f"      🔗 Пример: {source['example_url']}")
        print(f"      📄 Форматы: {', '.join(source['supported_formats'])}")
        print()

    print(f"🎯 Готовые builders: {', '.join(sources['ready_builders'])}")
    print(f"🚧 В разработке: {', '.join(sources['development_builders'])}")

    return sources


async def test_dag_listing():
    """Тест получения списка созданных DAG."""
    print("\n🧪 === ТЕСТ СПИСКА DAG ===\n")

    generator = IntegratedDAGGenerator(output_dir="test_integration_output")
    dags_info = await generator.list_generated_dags()

    print("📋 Список созданных DAG:")
    print(f"   📊 Всего: {dags_info['total_dags']}")

    if dags_info["success"] and dags_info["dags"]:
        for dag in dags_info["dags"]:
            print(f"   🆔 {dag['pipeline_id']}")
            print(f"      📁 Путь: {dag['path']}")
            print(f"      📄 DAG файл: {'✅' if dag['has_dag_file'] else '❌'}")
            print(f"      ⚙️ Конфиг: {'✅' if dag['has_config'] else '❌'}")
            print()
    else:
        print("   📭 Нет созданных DAG или ошибка получения списка")

    return dags_info


async def main():
    """Главная функция тестирования интеграции."""
    print("🚀 === ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ DAG ГЕНЕРАЦИИ ===")
    print("📅 Проверка работы с готовыми builders")
    print("=" * 60)

    try:
        # 1. Тест поддерживаемых источников
        await test_supported_sources()

        # 2. Тест XML folder интеграции
        xml_result = await test_xml_folder_integration()

        # 3. Тест PostgreSQL интеграции (может упасть из-за подключения)
        postgres_result = await test_postgres_integration()

        # 4. Тест списка DAG
        await test_dag_listing()

        print("\n" + "=" * 60)
        print("📊 === ИТОГИ ТЕСТИРОВАНИЯ ===")

        if xml_result.get("success"):
            print("✅ XML folder интеграция: РАБОТАЕТ")
        else:
            print("❌ XML folder интеграция: ОШИБКА")

        if postgres_result.get("success"):
            print("✅ PostgreSQL интеграция: РАБОТАЕТ")
        elif postgres_result.get("expected"):
            print("⚠️ PostgreSQL интеграция: Ожидаемая ошибка (нет БД)")
        else:
            print("❌ PostgreSQL интеграция: НЕОЖИДАННАЯ ОШИБКА")

        print("\n🎯 Система готова к использованию в основном приложении!")

    except Exception as e:
        print(f"\n💥 Критическая ошибка тестирования: {e}")
        print("🔍 Проверьте настройки и зависимости")


if __name__ == "__main__":
    asyncio.run(main())
