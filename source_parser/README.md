# запуск

C:\Users\eva\AppData\Local\Programs\Python\Python313\python.exe -m venv venv

venv\Scripts\activate.ps1

python -m pip install --upgrade pip

pip install -r requirements.txt

uvicorn main:app --reload

# тестовые запросы

curl "http://localhost:8000/get_meta?user_input=file:D:\MyProject\ict-hack-2025-doc\syn_csv"

curl "http://localhost:8000/get_meta?user_input=postgresql://user:password@localhost:5432/mydatabase"

curl "http://localhost:8000/get_meta?user_input=clickhouse://user:password@localhost:9000/mydatabase"

curl "http://localhost:8000/get_meta?user_input=kafka://broker1:9092,broker2:9092/my-topic?group.id=my-consumer-group"

curl "http://localhost:8000/get_meta?user_input=hdfs://namenode:8020/user/data"

curl "http://localhost:8000/get_meta?user_input=sparkstreaming"
