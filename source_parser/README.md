C:\Users\eva\AppData\Local\Programs\Python\Python313\python.exe -m venv venv

venv\Scripts\activate.ps1

python -m pip install --upgrade pip


pip install -r requirements.txt

uvicorn main:app --reload

curl "http://localhost:8000/get_meta?user_input=D:\MyProject\ict-hack-2025-doc\syn_csv"
