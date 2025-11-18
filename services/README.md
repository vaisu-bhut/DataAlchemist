# Independent Agentic Workflow System

## Overview

Multi-agent system where each agent is completely independent and ready for Cloud Run deployment.

## What Makes This "Agentic"?

Unlike traditional monolithic FastAPI apps, this system uses **autonomous agents** that communicate asynchronously through a pub/sub message bus. Here's what makes it agentic:

### 🤖 Key Agentic Features

**1. LangGraph State Machine Orchestration**
- The Master Agent uses **LangGraph** to manage complex workflows as state machines
- Each request flows through defined states: `route → wait_response → complete`
- Enables dynamic decision-making, retries, and conditional branching
- Traditional apps use rigid request/response - agents use stateful workflows

**2. Autonomous Agent Workers**
- Each agent (Ingest, Chat) operates **independently** with its own lifecycle
- Agents poll for work, process tasks, and publish results autonomously
- No direct coupling - agents don't know about each other
- Traditional apps have tightly coupled services with direct API calls

**3. Asynchronous Message-Based Communication**
- Agents communicate via **pub/sub topics** (not HTTP requests)
- Non-blocking: Master doesn't wait synchronously for workers
- Correlation IDs track requests across the distributed system
- Traditional apps use synchronous REST APIs that block and timeout

**4. Self-Contained Intelligence**
- Each agent has its own **decision-making logic** (LLM integration, retrieval strategies)
- Agents can adapt behavior based on context and state
- Ingest agent decides how to chunk, extract, and store data
- Chat agent decides which sources to use and how to synthesize responses

**5. Scalable & Resilient**
- Agents scale independently (e.g., 10 chat agents, 2 ingest agents)
- If one agent fails, others continue working
- New agent types can be added without modifying existing ones
- Traditional monoliths scale as a single unit and fail together

### 🆚 Traditional FastAPI App vs Agentic System

| Traditional Monolith | Agentic System |
|---------------------|----------------|
| Single FastAPI app with routes | Multiple autonomous agents |
| Synchronous request/response | Asynchronous message passing |
| Direct function calls | Pub/sub communication |
| Rigid control flow | State machine workflows (LangGraph) |
| Scales as one unit | Each agent scales independently |
| Tight coupling | Loose coupling via messages |
| Single point of failure | Fault isolation per agent |
| Hard to add new capabilities | Easy to add new agent types |

### 💡 Why This Architecture?

**For AI/LLM Workloads:**
- LLM calls are slow (5-30 seconds) - async messaging prevents timeouts
- Different tasks need different resources (chat needs more instances than ingest)
- Agents can retry, backoff, and handle LLM rate limits independently

**For Production Scale:**
- Deploy to Cloud Run with auto-scaling per agent
- Pay only for what you use (agents scale to zero)
- Update one agent without redeploying the entire system
- Add new agent types (e.g., "summarization agent") without touching existing code

**For Maintainability:**
- Each agent is a small, focused codebase
- Shared business logic in `/services/` prevents duplication
- Easy to test agents in isolation
- Clear separation of concerns

### 📝 Example: How a Chat Request Flows

**Traditional Monolith:**
```python
# Single app - everything blocks
@app.post("/chat")
def chat(query: str):
    embedding = llm.embed(query)        # Blocks 2s
    results = db.search(embedding)      # Blocks 1s
    response = llm.generate(results)    # Blocks 10s
    return response                     # Total: 13s blocking
```

**Agentic System:**
```python
# Master Agent (LangGraph workflow)
@app.post("/chat")
async def chat(query: str):
    # 1. Route through state machine
    state = {"request_type": "chat", "query": query}
    
    # 2. Publish to pub/sub (non-blocking)
    await pubsub.publish("chat.request", state)
    
    # 3. Master continues, doesn't block
    # 4. Chat agent polls, processes independently
    # 5. Master receives result when ready
    
    return await workflow.run(state)  # Async, can handle 1000s of requests
```

**Chat Agent (Autonomous Worker):**
```python
# Polls for work independently
async def poll_loop():
    while True:
        msg = await pubsub.poll("chat.request")
        if msg:
            # Process with full autonomy
            result = await retrieval_service.retrieve_and_respond(msg["query"])
            await pubsub.publish("chat.response", result)
```

**Benefits:**
- Master handles 1000s of concurrent requests (non-blocking)
- Chat agents scale independently (10 instances if needed)
- LLM timeouts don't crash the master
- Can add "summarization agent" without touching chat/ingest code

## Architecture Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT REQUEST                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Master Agent   │ ◄── LangGraph State Machine
                    │ (Port 8000)    │     • route → wait → complete
                    └────────┬───────┘
                             │
                             ▼
                    ┌────────────────┐
                    │   Pub/Sub      │ ◄── Message Bus
                    │  (Port 8001)   │     • Topics: ingest.*, chat.*
                    └────┬───────┬───┘     • Correlation IDs
                         │       │
           ┌─────────────┘       └─────────────┐
           ▼                                   ▼
    ┌──────────────┐                   ┌──────────────┐
    │ Ingest Agent │                   │  Chat Agent  │
    │ (Port 8002)  │                   │ (Port 8003)  │
    └──────┬───────┘                   └──────┬───────┘
           │                                   │
           │  Uses Shared:                     │  Uses Shared:
           │  • core/database.py               │  • core/database.py
           │  • core/llm_service.py            │  • core/llm_service.py
           │  • services/ingestion_service.py  │  • services/retrieval_service.py
           │  • models/schemas.py              │  • models/schemas.py
           │                                   │
           └───────────┬───────────────────────┘
                       ▼
              ┌────────────────┐
              │    Neo4j       │ ◄── Graph Database
              │   Database     │     • Vector embeddings
              └────────────────┘     • Knowledge graph
```

## Structure

```
services/
├── core/            # Shared core logic (database, LLM, config)
├── models/          # Shared data models and schemas
├── services/        # Shared business logic (ingestion, retrieval, PII)
├── agents/          # Agent implementations
│   ├── master/      # Orchestrator (LangGraph)
│   ├── ingest/      # Data processor
│   ├── chat/        # Query handler
│   └── shared/      # Shared agent utilities
├── pubsub/          # Message routing service
├── .env             # Configuration
└── README.md        # This file
```

## Agents

### 1. Master Agent (`agents/master/`)
- **Purpose**: API gateway with LangGraph orchestration
- **Port**: 8000
- **Dependencies**: Minimal (fastapi, langgraph, httpx)

### 2. Ingest Agent (`agents/ingest/`)
- **Purpose**: Process and store conversations
- **Port**: 8002
- **Dependencies**: Uses shared core, models, and services

### 3. Chat Agent (`agents/chat/`)
- **Purpose**: Handle queries and generate responses
- **Port**: 8003
- **Dependencies**: Uses shared core, models, and services

### 4. Analytics Agent (`agents/analytics/`) ⭐ NEW
- **Purpose**: Provides metrics and statistics API
- **Port**: 8004
- **Dependencies**: Uses shared core, models, and analytics service
- **Features**:
  - Summary metrics (conversations, issues, agents)
  - Issue distribution and trending
  - Agent performance tracking
  - Agent specialization analysis

### 5. Pub/Sub Service (`pubsub/`)
- **Purpose**: Message routing between agents
- **Port**: 8001
- **Dependencies**: Minimal (fastapi, structlog)


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

### Analytics ⭐ NEW
```bash
# Get summary metrics
curl http://localhost:8004/api/v1/analytics/summary

# Get top issues
curl http://localhost:8004/api/v1/analytics/issues/distribution?limit=10

# Get trending issues (last 7 days)
curl http://localhost:8004/api/v1/analytics/issues/trending?days=7

# Get agent performance
curl http://localhost:8004/api/v1/analytics/agents/performance?limit=10

# Get agent specialization
curl http://localhost:8004/api/v1/analytics/agents/agent123/specialization
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
