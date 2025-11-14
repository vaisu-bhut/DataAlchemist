FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY agents/ingest/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared code
COPY agents/shared /app/agents/shared
COPY core /app/core

# Copy agent code (includes models, services, etc.)
COPY agents/ingest /app/agents/ingest

WORKDIR /app/agents/ingest

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
