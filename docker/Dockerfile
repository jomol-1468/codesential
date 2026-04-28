# Base stage
FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc g++ && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir bandit semgrep

COPY app/ ./app/
COPY .env .env

# API server stage
FROM base AS api
EXPOSE 8000
CMD ["uvicorn", "app.api.webhook:app", \
     "--host", "0.0.0.0", "--port", "8000"]

# Celery worker stage
FROM base AS worker
CMD ["celery", "-A", "app.tasks", \
     "worker", "--loglevel=info", "--concurrency=2"]