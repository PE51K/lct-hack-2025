# Deployment Guide for Simple XML Test

Автоматически сгенерированная документация для развертывания ETL пайплайна.

## 📋 Обзор пайплайна

- **Pipeline ID:** `etl_simple_xml_test`
- **Владелец:** test_user
- **Команда:** test_team
- **Критичность:** medium
- **Ожидаемое время выполнения:** 13 минут

## 📁 Сгенерированные файлы

- `etl_simple_xml_test.py` - Основной DAG файл
- `etl_simple_xml_test_functions.py` - Модуль функций задач
- `etl_simple_xml_test_config.py` - Конфигурационный файл
- `requirements.txt` - Зависимости Python

## 🚀 Инструкции по развертыванию

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Копирование файлов в Airflow

Скопируйте следующие файлы в директорию DAGs Airflow:

```bash
cp etl_simple_xml_test.py $AIRFLOW_HOME/dags/
cp etl_simple_xml_test_functions.py $AIRFLOW_HOME/dags/
cp etl_simple_xml_test_config.py $AIRFLOW_HOME/dags/
```

### 3. Настройка подключений

Создайте следующие Airflow подключения:

#### Источник данных
- **Connection ID:** `etl_simple_xml_test_source`
- **Connection Type:** `folder`
- **Host/URI:** `file://d:/lct-hack-2025/backend/parsers/sample/XML/`

#### Целевое хранилище  
- **Connection ID:** `etl_simple_xml_test_target`
- **Connection Type:** `postgres`
- **Host:** (укажите ваш хост postgres)
- **Database:** `dwh`
- **Schema:** `public`

### 4. Создание целевой таблицы

```sql
-- Создайте таблицу public.Simple XML Test_data
-- в вашей целевой системе postgres

CREATE TABLE public.Simple XML Test_data (
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
airflow variables set etl_simple_xml_test_batch_size 1000
airflow variables set etl_simple_xml_test_parallel_workers 2
airflow variables set etl_simple_xml_test_notification_email "test_user@company.com"
```

### 6. Тестирование DAG

```bash
# Проверка синтаксиса DAG
airflow dags list | grep etl_simple_xml_test

# Тестовый запуск
airflow dags test etl_simple_xml_test $(date -d "yesterday" +%Y-%m-%d)

# Проверка задач
airflow tasks list etl_simple_xml_test
```

## ⚙️ Конфигурация ресурсов

### Минимальные требования
- **CPU:** 1.0 ядра
- **RAM:** 1824 МБ
- **Дисковое пространство:** 1024 МБ

### Настройки пула ресурсов Airflow

```bash
# Создание пула ресурсов
airflow pools set etl_simple_xml_test_pool 2 "Pool for etl_simple_xml_test"
```



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
- Логи Airflow: `$AIRFLOW_HOME/logs/dags/etl_simple_xml_test/`
- Логи приложения: `/var/log/airflow/dags/etl_simple_xml_test/`

## 📞 Поддержка

- **Владелец:** test_user
- **Команда:** test_team
- **Email для уведомлений:** test_user@company.com

---

*Документация создана автоматически 2025-09-30 22:02:19*
*Версия генератора: 2.0.0*
