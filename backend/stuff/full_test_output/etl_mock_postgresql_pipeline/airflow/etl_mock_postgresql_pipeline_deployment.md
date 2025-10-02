# Deployment Guide for Mock PostgreSQL Pipeline

Автоматически сгенерированная документация для развертывания ETL пайплайна.

## 📋 Обзор пайплайна

- **Pipeline ID:** `etl_mock_postgresql_pipeline`
- **Владелец:** test_user
- **Команда:** test_team
- **Критичность:** medium
- **Ожидаемое время выполнения:** 116 минут

## 📁 Сгенерированные файлы

- `etl_mock_postgresql_pipeline.py` - Основной DAG файл
- `etl_mock_postgresql_pipeline_functions.py` - Модуль функций задач
- `etl_mock_postgresql_pipeline_config.py` - Конфигурационный файл
- `requirements.txt` - Зависимости Python

## 🚀 Инструкции по развертыванию

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Копирование файлов в Airflow

Скопируйте следующие файлы в директорию DAGs Airflow:

```bash
cp etl_mock_postgresql_pipeline.py $AIRFLOW_HOME/dags/
cp etl_mock_postgresql_pipeline_functions.py $AIRFLOW_HOME/dags/
cp etl_mock_postgresql_pipeline_config.py $AIRFLOW_HOME/dags/
```

### 3. Настройка подключений

Создайте следующие Airflow подключения:

#### Источник данных
- **Connection ID:** `etl_mock_postgresql_pipeline_source`
- **Connection Type:** `postgres`
- **Host/URI:** `postgres://mock_user:mock_pass@localhost:5432/mock_db`

#### Целевое хранилище  
- **Connection ID:** `etl_mock_postgresql_pipeline_target`
- **Connection Type:** `postgres`
- **Host:** (укажите ваш хост postgres)
- **Database:** `dwh`
- **Schema:** `public`

### 4. Создание целевой таблицы

```sql
-- Создайте таблицу public.Mock PostgreSQL Pipeline_data
-- в вашей целевой системе postgres

CREATE TABLE public.Mock PostgreSQL Pipeline_data (
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
airflow variables set etl_mock_postgresql_pipeline_batch_size 1000
airflow variables set etl_mock_postgresql_pipeline_parallel_workers 1
airflow variables set etl_mock_postgresql_pipeline_notification_email "test_user@company.com"
```

### 6. Тестирование DAG

```bash
# Проверка синтаксиса DAG
airflow dags list | grep etl_mock_postgresql_pipeline

# Тестовый запуск
airflow dags test etl_mock_postgresql_pipeline $(date -d "yesterday" +%Y-%m-%d)

# Проверка задач
airflow tasks list etl_mock_postgresql_pipeline
```

## ⚙️ Конфигурация ресурсов

### Минимальные требования
- **CPU:** 4.0 ядра
- **RAM:** 3972 МБ
- **Дисковое пространство:** 1024 МБ

### Настройки пула ресурсов Airflow

```bash
# Создание пула ресурсов
airflow pools set etl_mock_postgresql_pipeline_pool 1 "Pool for etl_mock_postgresql_pipeline"
```

## 🤖 AI Рекомендации для развертывания

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
   - Проверьте путь: `postgres://mock_user:mock_pass@localhost:5432/mock_db`
   - Убедитесь в правах доступа к файлам

2. **Ошибки подключения к БД**
   - Проверьте настройки подключения в Airflow
   - Убедитесь в доступности целевой БД

3. **Превышение лимитов ресурсов**
   - Увеличьте память в конфигурации
   - Уменьшите размер батча

### Логи:
- Логи Airflow: `$AIRFLOW_HOME/logs/dags/etl_mock_postgresql_pipeline/`
- Логи приложения: `/var/log/airflow/dags/etl_mock_postgresql_pipeline/`

## 📞 Поддержка

- **Владелец:** test_user
- **Команда:** test_team
- **Email для уведомлений:** test_user@company.com

---

*Документация создана автоматически 2025-09-30 22:03:49*
*Версия генератора: 2.0.0*
