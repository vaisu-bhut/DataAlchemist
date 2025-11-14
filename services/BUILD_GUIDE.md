# Docker Build Guide

## Build Context

All Docker builds use `services/` as the build context.

## Dockerfiles

### 1. Pub/Sub Service
**Location:** `services/pubsub/Dockerfile`
**Build:** 
```bash
cd services
docker build -t pubsub:latest -f pubsub/Dockerfile .
```

### 2. Master Agent
**Location:** `services/agents/master/Dockerfile`
**Build:**
```bash
cd services
docker build -t master-agent:latest -f agents/master/Dockerfile .
```

### 3. Ingest Agent
**Location:** `services/agents/ingest/Dockerfile`
**Build:**
```bash
cd services
docker build -t ingest-agent:latest -f agents/ingest/Dockerfile .
```

### 4. Chat Agent
**Location:** `services/agents/chat/Dockerfile`
**Build:**
```bash
cd services
docker build -t chat-agent:latest -f agents/chat/Dockerfile .
```

## Directory Structure

```
services/
├── agents/
│   ├── shared/          # Shared utilities (copied to all agents)
│   ├── master/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── agent.py
│   │   └── main.py
│   ├── ingest/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── agent.py
│   │   ├── main.py
│   │   ├── models/
│   │   ├── services/
│   │   └── core/
│   └── chat/
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── agent.py
│       ├── main.py
│       ├── models/
│       ├── services/
│       └── core/
├── core/                # Shared core utilities
├── pubsub/
│   ├── Dockerfile
│   └── main.py
└── .dockerignore
```

## What Gets Copied

### Pub/Sub
- `pubsub/main.py`
- Dependencies installed directly in Dockerfile

### Master Agent
- `agents/master/requirements.txt` → Install dependencies
- `agents/shared/` → Shared utilities
- `agents/master/` → Agent code

### Ingest Agent
- `agents/ingest/requirements.txt` → Install dependencies
- `agents/shared/` → Shared utilities
- `core/` → Core utilities
- `agents/ingest/` → Agent code (includes models, services, core)

### Chat Agent
- `agents/chat/requirements.txt` → Install dependencies
- `agents/shared/` → Shared utilities
- `core/` → Core utilities
- `agents/chat/` → Agent code (includes models, services, core)

## Test Builds Locally

```bash
cd services

# Build all
docker build -t pubsub:test -f pubsub/Dockerfile .
docker build -t master-agent:test -f agents/master/Dockerfile .
docker build -t ingest-agent:test -f agents/ingest/Dockerfile .
docker build -t chat-agent:test -f agents/chat/Dockerfile .

# Clean up
docker rmi pubsub:test master-agent:test ingest-agent:test chat-agent:test
```

## GitHub Actions Build

The workflow builds from `services/` directory:

```yaml
working-directory: ./services
run: |
  IMAGE=us-east1-docker.pkg.dev/PROJECT/REPO/pubsub:latest
  docker build -t $IMAGE -f pubsub/Dockerfile .
  docker push $IMAGE
```

## Troubleshooting

### Error: "requirements.txt not found"
**Cause:** Wrong build context
**Fix:** Ensure you're in `services/` directory and using correct Dockerfile path

### Error: "models not found"
**Cause:** Trying to copy non-existent directory
**Fix:** Each agent has its own models directory inside `agents/{agent}/models/`

### Error: "shared not found"
**Cause:** Build context issue
**Fix:** Build from `services/` directory, not from agent subdirectory

## Build Order

No specific order required - all builds are independent.

## Dependencies

Each agent has its own `requirements.txt`:
- **Master:** FastAPI, LangGraph, httpx
- **Ingest:** FastAPI, Neo4j, Gemini, LangChain, LangGraph
- **Chat:** FastAPI, Neo4j, Gemini, LangChain, LangGraph
- **Pub/Sub:** FastAPI only (minimal)

---

**Always build from `services/` directory!** 🚀
