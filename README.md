# Webservice for Managing a User and Password Repository

## Running with Docker
To spin up the entire environment (including the API and the required infrastructure) using containers, execute the following commands in the project's root directory:

1. Open **Docker Desktop** and ensure it is running.
2. Stop and clear any existing containers and volumes:
   ```bash
   docker compose down -v
   ```
3. Build the necessary images and start the services:
   ```bash
   docker compose up --build
   ```

The API documentation and interactive testing interface (Swagger) will be available at:
👉 http://127.0.0.1:8001/docs

---

## Local Development (Visual Studio)
To run the application directly from your IDE or local environment:

1. Open the solution folder in Visual Studio.
2. Install the required dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Start the application using Uvicorn:
   ```bash
   uvicorn scripts.main:app --host 0.0.0.0 --port 8000
   ```

The API documentation and interactive testing interface (Swagger) will be available at:
👉 http://127.0.0.0:8000/docs

---

## Database
The database setup and initialization are fully automated.

---

## API Authentication
API keys for the two clients are generated as GUID strings and securely saved in the `clients` table.

---

## JSON Test Example
Use the following payload structure to test the user registration endpoint:

```json
{
  "username": "test",
  "full_name": "Test Tester",
  "email": "test@example.com",
  "mobile_number": "01 123 123",
  "language": "slo",
  "culture": "si",
  "password": "1234rewq"
}
```
