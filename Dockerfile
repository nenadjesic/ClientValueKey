FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the folder with the correct name (with "s")
COPY scripts/ ./scripts/

# Run the application from the direct context of the container
CMD ["uvicorn", "scripts.main:app", "--host", "0.0.0.0", "--port", "8000"]
