"""
Простой тест XML folder интеграции без внешних зависимостей.
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к DAG генерации
sys.path.append(str(Path(__file__).parent))

# Прямой импорт DAG системы
from dag_generation import ETLDAGGenerationSystem


async def test_xml_integration_simple():
    """Простой тест интеграции с XML папкой."""
    print("🧪 === ТЕСТ ИНТЕГРАЦИИ С XML ПАПКОЙ ===\n")

    # Создаем DAG систему
    dag_system = ETLDAGGenerationSystem(output_base_dir="simple_test_output")

    # Тестовый XML источник
    xml_source = "file://d:/lct-hack-2025/backend/parsers/sample/XML/"

    print(f"📂 Тестируем источник: {xml_source}")
    print("🔍 Проверяем доступность папки...")

    xml_path = Path("d:/lct-hack-2025/backend/parsers/sample/XML/")
    if xml_path.exists():
        xml_files = list(xml_path.glob("*.xml"))
        print(f"✅ Папка найдена, XML файлов: {len(xml_files)}")

        if xml_files:
            for xml_file in xml_files[:3]:  # Показываем первые 3
                size_kb = xml_file.stat().st_size / 1024
                print(f"   📄 {xml_file.name} ({size_kb:.1f} KB)")
        else:
            print("⚠️ XML файлы не найдены в папке")
            return False
    else:
        print("❌ Папка не найдена")
        return False

    print("\n🚀 Создаем ETL пайплайн...")

    try:
        result = await dag_system.create_complete_etl_pipeline(
            source_url=xml_source,
            pipeline_name="Simple XML Test",
            owner="test_user",
            team="test_team",
            description="Тест интеграции XML с готовыми builders",
        )

        print("\n📊 === РЕЗУЛЬТАТЫ ===")

        if result.get("success") or result.get("pipeline_id"):
            print("✅ Пайплайн успешно создан!")
            print(f"🆔 Pipeline ID: {result.get('pipeline_id', 'N/A')}")
            print(f"📁 Выходная директория: {result.get('output_directory', 'N/A')}")

            # Проверяем созданные файлы
            files = result.get("files", {})
            if files:
                print("\n📄 Созданные файлы:")
                for file_type, file_path in files.items():
                    if file_path and Path(file_path).exists():
                        file_size = Path(file_path).stat().st_size / 1024
                        print(f"   ✅ {file_type}: {file_path} ({file_size:.1f} KB)")
                    else:
                        print(f"   ❌ {file_type}: файл не найден")

            # AI рекомендации
            ai_recs = result.get("ai_recommendations", [])
            if ai_recs:
                print(f"\n🤖 AI рекомендации: {len(ai_recs)}")
                for i, rec in enumerate(ai_recs[:2], 1):  # Показываем первые 2
                    title = rec.title if hasattr(rec, "title") else str(rec)
                    print(f"   {i}. {title}")

            print(
                f"\n⏱️ Ожидаемое время выполнения: {result.get('estimated_runtime_minutes', 0)} мин"
            )

            return True

        else:
            print("❌ Ошибка создания пайплайна")
            print(f"🔍 Причина: {result.get('error', 'Неизвестная ошибка')}")
            return False

    except Exception as e:
        print(f"💥 Исключение при создании пайплайна: {e}")
        print(f"📝 Тип ошибки: {type(e).__name__}")

        # Дополнительная диагностика
        import traceback

        print("\n🔬 Подробная трассировка:")
        traceback.print_exc()

        return False


async def main():
    """Главная функция."""
    print("🎯 === ПРОСТОЙ ТЕСТ ИНТЕГРАЦИИ ===")
    print("Проверка работы DAG генерации с XML folder builder")
    print("=" * 50)

    success = await test_xml_integration_simple()

    print("\n" + "=" * 50)
    if success:
        print("🎉 ТЕСТ ПРОЙДЕН УСПЕШНО!")
        print("✅ Интеграция с XML builders работает")
        print("🚀 Система готова к использованию")
    else:
        print("❌ ТЕСТ НЕ ПРОЙДЕН")
        print("🔧 Требуется дополнительная настройка")


if __name__ == "__main__":
    asyncio.run(main())
