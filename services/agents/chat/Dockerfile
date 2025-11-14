FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy and install requirements from root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared code
COPY agents/shared /app/agents/shared
COPY models /app/models
COPY core /app/core
COPY services /app/services

# Copy agent code
COPY agents/chat /app/agents/chat

WORKDIR /app/agents/chat

EXPOSE 8003

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
