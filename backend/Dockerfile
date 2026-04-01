FROM python:3.10-slim

WORKDIR /app

# Ensure we have build essentials for some python dependencies and pg drivers
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend into /app/backend
COPY . /app/backend

# Use /app as the Python path so "backend.main" naturally resolves
ENV PYTHONPATH=/app

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
