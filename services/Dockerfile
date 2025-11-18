FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y gcc curl supervisor && \
    rm -rf /var/lib/apt/lists/*

# Copy shared code
COPY core /app/core
COPY models /app/models
COPY services /app/services

# Copy all agents
COPY agents /app/agents
COPY pubsub /app/pubsub

# Install all dependencies (combine all requirements)
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    httpx==0.25.1 \
    structlog==23.2.0 \
    pydantic==2.5.0 \
    pydantic-settings==2.1.0 \
    langgraph==0.0.20 \
    langchain==0.1.0 \
    neo4j==5.14.1 \
    google-generativeai==0.3.1

# Create supervisor config
RUN mkdir -p /var/log/supervisor

COPY <<EOF /etc/supervisor/conf.d/supervisord.conf
[supervisord]
nodaemon=true
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid

[program:pubsub]
command=uvicorn main:app --host 0.0.0.0 --port 8001
directory=/app/pubsub
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:master-agent]
command=uvicorn main:app --host 0.0.0.0 --port 8000
directory=/app/agents/master
environment=PUBSUB_URL="http://localhost:8001"
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:ingest-agent]
command=uvicorn main:app --host 0.0.0.0 --port 8002
directory=/app/agents/ingest
environment=PUBSUB_URL="http://localhost:8001"
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:chat-agent]
command=uvicorn main:app --host 0.0.0.0 --port 8003
directory=/app/agents/chat
environment=PUBSUB_URL="http://localhost:8001"
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:analytics-agent]
command=uvicorn main:app --host 0.0.0.0 --port 8004
directory=/app/agents/analytics
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
EOF

# Expose all ports
EXPOSE 8000 8001 8002 8003 8004

# Health check script
COPY <<'EOF' /app/healthcheck.sh
#!/bin/bash
curl -f http://localhost:8001/health && \
curl -f http://localhost:8000/health && \
curl -f http://localhost:8002/health && \
curl -f http://localhost:8003/health && \
curl -f http://localhost:8004/health
EOF

RUN chmod +x /app/healthcheck.sh

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD /app/healthcheck.sh

# Start supervisor to run all services
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
