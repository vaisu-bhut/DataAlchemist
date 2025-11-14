FROM python:3.11-slim

WORKDIR /app

# Install minimal dependencies for pubsub
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    structlog==23.2.0

# Copy service code
COPY pubsub/main.py .

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
