

- Start sa local db

python -m pip install -r requirements.txt
uvicorn scripts.main:app --host 0.0.0.0 --port 8000

http://127.0.0.1:8000/docs



{
  "username": "epi",
  "full_name": "Nenad Jesic",
  "email": "nenad@example.com",
  "mobile_number": "123 123",
  "language": "slo",
  "culture": "si",
  "password": "1234rewq"
}

- Docker 

docker-compose up --build
http://127.0.0.1:8001/docs


