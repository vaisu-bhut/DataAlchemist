# Independent Agentic Workflow System

## Overview

Multi-agent system where each agent is completely independent and ready for Cloud Run deployment.

## Structure

```
services/
├── agents/
│   ├── master/      # Orchestrator (LangGraph)
│   ├── ingest/      # Data processor (self-contained)
│   └── chat/        # Query handler (self-contained)
├── pubsub/          # Message routing
├── .env             # Configuration
└── README.md        # This file
```

## Agents

### 1. Master Agent (`agents/master/`)
- **Purpose**: API gateway with LangGraph orchestration
- **Port**: 8000
- **Dependencies**: Minimal (fastapi, langgraph, httpx)
- **Size**: ~200 MB

### 2. Ingest Agent (`agents/ingest/`)
- **Purpose**: Process and store conversations
- **Port**: 8002
- **Dependencies**: Full stack (bundled: core, models, services)
- **Size**: ~800 MB
- **Self-contained**: Yes

### 3. Chat Agent (`agents/chat/`)
- **Purpose**: Handle queries and generate responses
- **Port**: 8003
- **Dependencies**: Full stack (bundled: core, models, services)
- **Size**: ~800 MB
- **Self-contained**: Yes

### 4. Pub/Sub Service (`pubsub/`)
- **Purpose**: Message routing between agents
- **Port**: 8001
- **Dependencies**: Minimal (fastapi, structlog)
- **Size**: ~150 MB


## Configuration

Edit `.env`:
```bash
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
GEMINI_API_KEY=your_key
GEMINI_MODEL_NAME=gemini-2.5-pro
GEMINI_EMBEDDING_MODEL=models/text-embedding-004
SECRET_KEY=your-secret
CHUNK_SIZE=2000
SIMILARITY_THRESHOLD=0.85
CONFIDENCE_THRESHOLD=0.7
MAX_RETRIEVAL_RESULTS=10
```

## Build & Deploy Each Agent

### Master Agent
```bash
cd agents/master
docker build -t master-agent .
docker run -p 8000:8000 -e PUBSUB_URL=http://pubsub:8001 master-agent
```

### Ingest Agent
```bash
cd agents/ingest
docker build -t ingest-agent .
docker run -p 8002:8002 --env-file ../../.env ingest-agent
```

### Chat Agent
```bash
cd agents/chat
docker build -t chat-agent .
docker run -p 8003:8003 --env-file ../../.env chat-agent
```

### Pub/Sub
```bash
cd pubsub
docker build -t pubsub-service .
docker run -p 8001:8001 pubsub-service
```

## Cloud Run Deployment

Each agent deploys independently:

```bash
# Set project
export PROJECT_ID=your-gcp-project
export REGION=us-central1

# Deploy Pub/Sub
cd pubsub
gcloud builds submit --tag gcr.io/$PROJECT_ID/pubsub
gcloud run deploy pubsub --image gcr.io/$PROJECT_ID/pubsub --region $REGION --port 8001

# Deploy Master
cd ../agents/master
gcloud builds submit --tag gcr.io/$PROJECT_ID/master
gcloud run deploy master --image gcr.io/$PROJECT_ID/master --region $REGION --port 8000

# Deploy Ingest
cd ../ingest
gcloud builds submit --tag gcr.io/$PROJECT_ID/ingest
gcloud run deploy ingest --image gcr.io/$PROJECT_ID/ingest --region $REGION --port 8002 \
  --set-secrets NEO4J_URI=neo4j-uri:latest,GEMINI_API_KEY=gemini-key:latest

# Deploy Chat
cd ../chat
gcloud builds submit --tag gcr.io/$PROJECT_ID/chat
gcloud run deploy chat --image gcr.io/$PROJECT_ID/chat --region $REGION --port 8003 \
  --set-secrets NEO4J_URI=neo4j-uri:latest,GEMINI_API_KEY=gemini-key:latest
```

## API Usage

### Ingest
```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{"conversations": [{"conversation_id": "1", "customer_id": "c1", "agent_id": "a1", "messages": [{"role": "customer", "content": "help"}]}]}'
```

### Chat
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I get help?"}'
```

## Scaling

Each agent scales independently on Cloud Run:

```bash
gcloud run services update ingest --min-instances 1 --max-instances 10
gcloud run services update chat --min-instances 2 --max-instances 20
```

## Benefits

✅ **Independent**: Each agent is self-contained
✅ **Scalable**: Scale each agent independently
✅ **Isolated**: Fault isolation between agents
✅ **Cloud Ready**: Deploy to Cloud Run immediately
✅ **Cost Optimized**: Pay only for what you use

## Architecture

```
Client → Master Agent (LangGraph) → Pub/Sub → Ingest/Chat Agents → Neo4j
```

Each agent:
- Builds independently
- Deploys independently
- Scales independently (0 to N instances)
- Fails independently (no cascading failures)

---

**Ready for Cloud Run deployment!** 🚀


## Quick Deploy to Cloud Run

### Prerequisites
- GCP account with billing enabled
- gcloud CLI installed
- Neo4j Aura database

### One-Command Deploy

```bash
# 1. Setup secrets (first time only)
chmod +x setup-secrets.sh
./setup-secrets.sh

# 2. Deploy all agents
chmod +x deploy.sh
./deploy.sh
```

### Manual Deploy

See `DEPLOY_TO_CLOUD_RUN.md` for detailed step-by-step instructions.

## Files

- **README.md** - This file (main guide)
- **DEPLOY_TO_CLOUD_RUN.md** - Detailed deployment guide
- **deploy.sh** - Automated deployment script
- **setup-secrets.sh** - Setup GCP secrets
- **.env** - Local configuration template

## Support

For deployment issues:
1. Check `DEPLOY_TO_CLOUD_RUN.md`
2. View Cloud Run logs: `gcloud run services logs read SERVICE_NAME`
3. Check service status: `gcloud run services describe SERVICE_NAME`
