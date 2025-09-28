# запуск проекта

docker compose -f 'docker-compose.pg.yaml' up

подключаемся через Dbeaver, создаем таблицу, заполняем данные

запускаем проект

выполняем тестовый curl 

# запуск

C:\Users\eva\AppData\Local\Programs\Python\Python313\python.exe -m venv venv

venv\Scripts\activate.ps1

python -m pip install --upgrade pip

pip install -r requirements.txt

uvicorn main:app --reload

# тестовые запросы

curl "http://localhost:8000/get_meta?user_input=подключись к postgresql://myuser:mypassword@localhost:5432/mydatabase и загрузи таблицу ticket_data"

# код для создания таблицы в pg

CREATE TABLE ticket_data (
    created TIMESTAMP WITH TIME ZONE,
    order_status VARCHAR(50),
    ticket_status VARCHAR(50),
    ticket_price DECIMAL(10,2),
    visitor_category TEXT,
    event_id INTEGER,
    is_active BOOLEAN,
    valid_to DATE,
    count_visitor INTEGER,
    is_entrance BOOLEAN,
    is_entrance_mdate TIMESTAMP WITH TIME ZONE,
    event_name TEXT,
    event_kind_name TEXT,
    spot_id INTEGER,
    spot_name TEXT,
    museum_name TEXT,
    start_datetime TIMESTAMP WITHOUT TIME ZONE,
    ticket_id BIGINT,
    update_timestamp TIMESTAMP WITH TIME ZONE,
    client_name TEXT,
    name TEXT,
    surname TEXT,
    client_phone TEXT,
    museum_inn VARCHAR(20),
    birthday_date DATE,
    order_number VARCHAR(100),
    ticket_number UUID
);
GO
-- Создание первичного ключа
ALTER TABLE ticket_data ADD COLUMN id BIGSERIAL PRIMARY KEY;

-- Создание некластеризованных индексов для часто используемых полей
CREATE INDEX idx_ticket_data_ticket_id ON ticket_data (ticket_id);
CREATE INDEX idx_ticket_data_event_id ON ticket_data (event_id);
CREATE INDEX idx_ticket_data_spot_id ON ticket_data (spot_id);
CREATE INDEX idx_ticket_data_start_datetime ON ticket_data (start_datetime);
CREATE INDEX idx_ticket_data_order_status ON ticket_data (order_status);
CREATE INDEX idx_ticket_data_museum_inn ON ticket_data (museum_inn);

-- Комментарии к таблице и колонкам
COMMENT ON TABLE ticket_data IS 'Данные о билетах и заказах из CSV';
COMMENT ON COLUMN ticket_data.id IS 'Автоинкрементный первичный ключ';
COMMENT ON COLUMN ticket_data.ticket_id IS 'Идентификатор билета';
COMMENT ON COLUMN ticket_data.ticket_number IS 'Уникальный идентификатор билета в формате UUID';

# код для вставки тестовых данных

INSERT INTO ticket_data (
    created, order_status, ticket_status, ticket_price, visitor_category, 
    event_id, is_active, valid_to, count_visitor, is_entrance, 
    is_entrance_mdate, event_name, event_kind_name, spot_id, spot_name, 
    museum_name, start_datetime, ticket_id, update_timestamp, client_name, 
    name, surname, client_phone, museum_inn, birthday_date, order_number, 
    ticket_number
) VALUES 
(
    '2021-01-01T16:01:14.583+03:00', 'PAID', 'PAID', 0.0, 
    'Обучающиеся по очной форме обучения в государственных образовательных учреждениях и негосударственных образовательных организациях, имеющих государственную аккредитацию, по программам начального общего, основного общего, среднего (полного) общего образования', 
    0000, true, '2021-01-11', 1, true, 
    '2021-01-11T19:14:45.427+03:00', 'Бальный танец', 
    'консультация, методическое занятие, семинар, тренинг', 000000, 
    'Шверника ул. 13, корпус 2', 
    'Государственное бюджетное учреждение культуры города Москвы «Центр культуры и досуга «Академический»', 
    '2021-01-11 17:00:00', 1778482, 
    '2021-01-11T16:01:15.682+03:00', 'Иван Иванов', 'Иван', 
    'Иванов', '79859482165', '3832203597', NULL, 
    '00000-000000', '00000000-0000-0000-0000-000000000000'
)