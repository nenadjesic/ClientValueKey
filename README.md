# Solution Webservice for managing a repository of users and their passwords


## Running with Docker
To spin up the entire environment (including the API and required infrastructure) using containers, execute the following command in the project's root directory:

### Run Docekr desktop  
### docker compose down -v 
### docker compose up --build

This command automatically builds the necessary images and starts the defined services.

The API documentation and testing interface (Swagger) will be available at: 
👉 [http://127.0.0.1:8001/docs]


## Local Development (Visual Studio)
   
### To run the application directly from your IDE:

* Open the solution folder in Visual Studio.
### python -m pip install -r requirements.txt
### uvicorn scripts.main:app --host 0.0.0.0 --port 8000

The API documentation and testing interface (Swagger) will be available at:
👉 [http://127.0.0.1:8000/doc]

# Database
Is automated

# API KEY
For two client key is generated as gui string and saved in table clients


# Json example for test

{
  "username": "test",
  "full_name": "Test Tester",
  "email": "test@example.com",
  "mobile_number": "01 123 123",
  "language": "slo",
  "culture": "si",
  "password": "1234rewq"
}


