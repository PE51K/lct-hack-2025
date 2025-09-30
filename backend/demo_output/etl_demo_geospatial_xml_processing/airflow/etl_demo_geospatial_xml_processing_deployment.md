# Deployment Guide for Demo Geospatial XML Processing

Автоматически сгенерированная документация для развертывания ETL пайплайна.

## 📋 Обзор пайплайна

- **Pipeline ID:** `etl_demo_geospatial_xml_processing`
- **Владелец:** demo_user
- **Команда:** demo_team
- **Критичность:** medium
- **Ожидаемое время выполнения:** 34 минут

## 📁 Сгенерированные файлы

- `etl_demo_geospatial_xml_processing.py` - Основной DAG файл
- `etl_demo_geospatial_xml_processing_functions.py` - Модуль функций задач
- `etl_demo_geospatial_xml_processing_config.py` - Конфигурационный файл
- `requirements.txt` - Зависимости Python

## 🚀 Инструкции по развертыванию

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Копирование файлов в Airflow

Скопируйте следующие файлы в директорию DAGs Airflow:

```bash
cp etl_demo_geospatial_xml_processing.py $AIRFLOW_HOME/dags/
cp etl_demo_geospatial_xml_processing_functions.py $AIRFLOW_HOME/dags/
cp etl_demo_geospatial_xml_processing_config.py $AIRFLOW_HOME/dags/
```

### 3. Настройка подключений

Создайте следующие Airflow подключения:

#### Источник данных
- **Connection ID:** `etl_demo_geospatial_xml_processing_source`
- **Connection Type:** `folder`
- **Host/URI:** `file://d:/lct-hack-2025/backend/parsers/sample/XML/`

#### Целевое хранилище  
- **Connection ID:** `etl_demo_geospatial_xml_processing_target`
- **Connection Type:** `postgres`
- **Host:** (укажите ваш хост postgres)
- **Database:** `dwh`
- **Schema:** `public`

### 4. Создание целевой таблицы

```sql
-- Создайте таблицу public.Demo Geospatial XML Processing_data
-- в вашей целевой системе postgres

CREATE TABLE public.Demo Geospatial XML Processing_data (
    record_id VARCHAR(50) PRIMARY KEY,
    coordinate_system VARCHAR(20),
    purpose TEXT,
    coordinate_count INTEGER,
    sample_coordinates TEXT,
    processed_at TIMESTAMP,
    source_file VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5. Настройка переменных Airflow

```bash
# Установка переменных конфигурации
airflow variables set etl_demo_geospatial_xml_processing_batch_size 1000
airflow variables set etl_demo_geospatial_xml_processing_parallel_workers 4
airflow variables set etl_demo_geospatial_xml_processing_notification_email "demo_user@company.com"
```

### 6. Тестирование DAG

```bash
# Проверка синтаксиса DAG
airflow dags list | grep etl_demo_geospatial_xml_processing

# Тестовый запуск
airflow dags test etl_demo_geospatial_xml_processing $(date -d "yesterday" +%Y-%m-%d)

# Проверка задач
airflow tasks list etl_demo_geospatial_xml_processing
```

## ⚙️ Конфигурация ресурсов

### Минимальные требования
- **CPU:** 4.0 ядра
- **RAM:** 2765 МБ
- **Дисковое пространство:** 1024 МБ

### Настройки пула ресурсов Airflow

```bash
# Создание пула ресурсов
airflow pools set etl_demo_geospatial_xml_processing_pool 4 "Pool for etl_demo_geospatial_xml_processing"
```

## 🤖 AI Рекомендации для развертывания

### Оптимизация обработки сложных XML данных
Рекомендуется использовать стриминговый парсинг и увеличить объем памяти для обработки сложных XML структур.

**Усилия по внедрению:** medium
**Ожидаемые улучшения:** {'processing_speed': 2.3, 'memory_efficiency': 1.8}

**Шаги внедрения:**
- Включить стриминговый XML парсинг
- Увеличить память до 4GB для transformation задач
- Использовать батчи размером 500 записей
- Включить промежуточное кеширование результатов

### Увеличение ресурсов для больших объемов данных
Для обработки больших объемов данных рекомендуется использовать параллельную обработку.

**Усилия по внедрению:** low
**Ожидаемые улучшения:** {'processing_time': 0.6, 'throughput': 2.1}

**Шаги внедрения:**
- Увеличить количество параллельных воркеров до 4
- Выделить 8GB оперативной памяти
- Использовать SSD для временных файлов



## 📊 Мониторинг и метрики

### Ключевые метрики для отслеживания:
- Количество обработанных записей
- Время выполнения каждой задачи
- Использование ресурсов (CPU/RAM)
- Качество данных (completeness, accuracy)
- Количество ошибок

### Настройка алертов:
- Email уведомления при сбоях: True
- SLA: не установлено минут

## 🔧 Устранение неполадок

### Частые проблемы:

1. **Файлы источника недоступны**
   - Проверьте путь: `file://d:/lct-hack-2025/backend/parsers/sample/XML/`
   - Убедитесь в правах доступа к файлам

2. **Ошибки подключения к БД**
   - Проверьте настройки подключения в Airflow
   - Убедитесь в доступности целевой БД

3. **Превышение лимитов ресурсов**
   - Увеличьте память в конфигурации
   - Уменьшите размер батча

### Логи:
- Логи Airflow: `$AIRFLOW_HOME/logs/dags/etl_demo_geospatial_xml_processing/`
- Логи приложения: `/var/log/airflow/dags/etl_demo_geospatial_xml_processing/`

## 📞 Поддержка

- **Владелец:** demo_user
- **Команда:** demo_team
- **Email для уведомлений:** demo_user@company.com

---

*Документация создана автоматически 2025-09-30 20:33:21*
*Версия генератора: 2.0.0*
