# Independent Agentic Workflow System

## Overview

A production-ready multi-agent system for intelligent customer support that uses autonomous agents communicating through pub/sub messaging. Each agent is independently deployable to Google Cloud Run with automatic scaling, fault isolation, and zero-downtime updates.

The system ingests customer support conversations, extracts canonical issues and solutions using LLMs, stores them in a Neo4j graph database with vector embeddings, and provides intelligent query responses with source citations.

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

## Project Structure

```
services/
├── core/                          # Shared infrastructure
│   ├── config.py                  # Settings with JSON secret parsing
│   ├── database.py                # Neo4j async connection & schema
│   ├── llm_service.py             # Gemini API wrapper (embeddings, extraction, synthesis)
│   └── secrets_loader.py          # GCP Secret Manager integration
│
├── models/                        # Data models
│   └── schemas.py                 # Pydantic models for all entities
│
├── services/                      # Business logic (shared by agents)
│   ├── ingestion_service.py       # Conversation processing & storage
│   ├── retrieval_service.py       # Vector search & response generation
│   ├── analytics_service.py       # Metrics & statistics queries
│   └── pii_redactor.py            # PII detection & redaction
│
├── agents/                        # Independent agent services
│   ├── master/                    # API Gateway + LangGraph orchestrator
│   │   ├── main.py                # FastAPI app (port 8000)
│   │   ├── agent.py               # LangGraph state machine workflow
│   │   ├── Dockerfile             # Minimal dependencies
│   │   └── requirements.txt
│   │
│   ├── ingest/                    # Conversation ingestion worker
│   │   ├── main.py                # Polls ingest.request topic
│   │   ├── Dockerfile             # Includes core + services
│   │   └── requirements.txt
│   │
│   ├── chat/                      # Query response worker
│   │   ├── main.py                # Polls chat.request topic
│   │   ├── Dockerfile             # Includes core + services
│   │   └── requirements.txt
│   │
│   ├── analytics/                 # Metrics API
│   │   ├── main.py                # REST API for analytics (port 8004)
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── shared/                    # Shared agent utilities
│       └── load_secrets.py        # Secret loading helper
│
├── pubsub/                        # Message bus service
│   ├── main.py                    # FastAPI pub/sub server (port 8001)
│   ├── service.py                 # In-memory queue with peek/acknowledge
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml             # Local development orchestration
├── Dockerfile                     # All-in-one container (supervisor)
├── .env                           # Local configuration
├── generate_large_sample.py       # Test data generator
└── README.md                      # This file
```

## Agent Services

### 1. Master Agent (`agents/master/`) - Port 8000
**Role**: API Gateway & Orchestrator

**Technology**: FastAPI + LangGraph state machine

**Workflow**:
- Receives HTTP requests from clients
- Creates correlation IDs for request tracking
- Publishes requests to pub/sub topics
- Uses LangGraph workflow: `route → wait_response → complete`
- Polls for responses using peek/acknowledge pattern
- Returns results to clients

**Key Features**:
- Stateful workflow management with LangGraph
- Non-blocking async request handling
- Timeout management (300s default)
- Proxies analytics requests to analytics agent

**Dependencies**: Minimal (fastapi, langgraph, httpx, structlog)

---

### 2. Ingest Agent (`agents/ingest/`) - Port 8002
**Role**: Conversation Processing Worker

**Process Flow**:
1. Polls `ingest.request` topic continuously
2. Receives conversation data with messages
3. Redacts PII (emails, phones, SSN, credit cards, IPs)
4. Chunks text if needed (2000 char chunks)
5. Calls Gemini to extract canonical issues & solutions
6. Generates embeddings for vector search
7. Stores in Neo4j:
   - Customer & Agent nodes
   - Conversation nodes with raw text
   - Issue nodes with embeddings
   - Solution nodes with embeddings
   - Relationships: BELONGS_TO, HANDLED_BY, CONTAINS_ISSUE, CONTAINS_SOLUTION
8. Publishes result to `ingest.response` topic

**Key Features**:
- Automatic PII redaction with regex patterns
- LLM-based canonical data extraction
- Vector similarity deduplication (merges similar issues)
- Graceful degradation if Neo4j unavailable
- Batch processing support

**Dependencies**: Full stack (core, services, models, neo4j, google-generativeai)

---

### 3. Chat Agent (`agents/chat/`) - Port 8003
**Role**: Query Response Worker

**Process Flow**:
1. Polls `chat.request` topic continuously
2. Receives query and customer_id
3. Generates query embedding using Gemini
4. Performs vector similarity search in Neo4j:
   - Searches issue_embeddings index
   - Searches solution_embeddings index
   - Retrieves top K candidates (configurable)
5. Ranks candidates using composite scoring:
   - Similarity score (40%)
   - Quality score (30%)
   - Human review bonus (20%)
   - Recency bonus (10%)
6. Filters by confidence threshold (0.7 default)
7. Calls Gemini to synthesize response with citations
8. Determines if human escalation needed (confidence < 0.7)
9. Publishes result to `chat.response` topic

**Key Features**:
- Vector similarity search with cosine distance
- Multi-factor candidate ranking
- Source citation with conversation snippets
- Automatic escalation logic
- Confidence scoring

**Dependencies**: Full stack (core, services, models, neo4j, google-generativeai)

---

### 4. Analytics Agent (`agents/analytics/`) - Port 8004
**Role**: Metrics & Statistics API

**Endpoints**:
- `GET /api/v1/analytics/summary` - High-level metrics
- `GET /api/v1/analytics/issues/distribution` - Top issues by occurrence
- `GET /api/v1/analytics/agents/performance` - Agent performance metrics
- `GET /api/v1/analytics/customers` - Customer list with conversation counts
- `GET /api/v1/analytics/customers/{id}/issues` - Customer issue history
- `GET /api/v1/analytics/resolution-time` - Resolution time statistics
- `GET /api/v1/analytics/escalation` - AI vs human resolution analytics

**Metrics Provided**:
- Total conversations, issues, solutions, agents, customers
- Average resolution time
- Issue distribution and trending
- Agent performance and specialization
- Customer issue history
- Escalation rates and AI efficiency
- Human effort saved calculations

**Dependencies**: Core + analytics service (neo4j, pydantic)

---

### 5. Pub/Sub Service (`pubsub/`) - Port 8001
**Role**: Message Bus for Inter-Agent Communication

**Implementation**: In-memory async queues with deque

**API**:
- `POST /publish` - Publish message to topic
- `GET /poll/{topic}` - Poll and remove message (legacy)
- `GET /peek/{topic}?correlation_id=X` - Peek without removing
- `POST /acknowledge` - Remove specific message by correlation_id

**Features**:
- Peek/acknowledge pattern for reliable delivery
- Correlation ID filtering
- Message TTL (5 minutes)
- Automatic cleanup of expired messages
- Topic-based routing

**Topics**:
- `ingest.request` / `ingest.response`
- `chat.request` / `chat.response`

**Dependencies**: Minimal (fastapi, structlog)


## Core Shared Components

### Database Layer (`core/database.py`)
- **Neo4jConnection**: Async driver wrapper with connection pooling
- **Schema Management**: Auto-creates constraints and vector indexes
- **Constraints**: Unique IDs for Conversation, Issue, Solution, Customer, Agent
- **Vector Indexes**: 
  - `issue_embeddings` - 768-dim cosine similarity
  - `solution_embeddings` - 768-dim cosine similarity
- **Health Checks**: Connection verification and retry logic
- **Query Execution**: Async query/write methods with error handling

### LLM Service (`core/llm_service.py`)
- **GeminiService**: Wrapper for Google Generative AI
- **Embedding Generation**: Text-to-vector using `text-embedding-004` (768 dimensions)
- **Canonical Data Extraction**: Structured JSON extraction from conversations
  - Issues: canonical description, one-liner, tags, intent
  - Solutions: steps, confidence, one-liner
  - Overall confidence and summary
- **Response Synthesis**: Context-aware response generation with citations
- **Cosine Similarity**: Vector comparison utility

### Business Logic Services

**IngestionService** (`services/ingestion_service.py`):
- Conversation processing pipeline
- PII redaction integration
- Text chunking for long conversations
- LLM extraction orchestration
- Neo4j storage with relationships
- Vector similarity deduplication

**RetrievalService** (`services/retrieval_service.py`):
- Query embedding generation
- Dual vector search (issues + solutions)
- Composite ranking algorithm
- Confidence filtering
- Response synthesis with LLM
- Source reference building

**AnalyticsService** (`services/analytics_service.py`):
- Cypher query builders for metrics
- Aggregation and statistics
- Time-based analytics
- Customer journey tracking
- Agent performance calculations

**PIIRedactor** (`services/pii_redactor.py`):
- Regex-based PII detection
- Patterns: email, phone, SSN, credit card, IP address
- Conversation-wide redaction
- Metadata sanitization

## Configuration

### Local Development
Create a `.env` file with:
- Neo4j connection details (URI, user, password)
- Google Gemini API key and model names
- Application settings (chunk size, thresholds, etc.)

### Cloud Deployment
The system supports both individual environment variables and JSON secrets from GCP Secret Manager. The `core/config.py` automatically parses JSON secrets (DATABASE_CREDENTIALS, API_KEYS) and falls back to individual environment variables for flexibility.

## Local Development

### Using Docker Compose (Recommended)
Start all services with `docker-compose up --build`. Services will be available at:
- Master Agent: http://localhost:8000
- Pub/Sub: http://localhost:8001
- Ingest Agent: http://localhost:8002
- Chat Agent: http://localhost:8003
- Analytics Agent: http://localhost:8004

### Building Individual Agents
Each agent has its own Dockerfile and can be built independently. The Dockerfiles use multi-stage builds and copy shared code (core, models, services) into each container.

### All-in-One Container
For testing, the root Dockerfile uses supervisor to run all services in a single container. This is useful for development but not recommended for production.

## Cloud Deployment

For production deployment to Google Cloud Run with Terraform, see the `terraform/` directory. The Terraform configuration handles:
- Cloud Run service deployment for all agents
- GCP Secret Manager integration
- VPC networking and service connectivity
- IAM roles and permissions
- Auto-scaling configuration

## API Usage

All requests go through the Master Agent (port 8000), which orchestrates the workflow.

### Ingest Conversations

Send POST requests to `/api/v1/ingest` with conversation data including messages, customer_id, agent_id, and timestamps. The system will:
1. Redact PII from messages
2. Extract canonical issues and solutions using LLM
3. Generate embeddings for vector search
4. Store in Neo4j with relationships
5. Return processing results with batch_id

### Query (Chat)

Send POST requests to `/api/v1/chat` with a query and customer_id. The system will:
1. Generate query embedding
2. Perform vector similarity search in Neo4j
3. Rank candidates using composite scoring
4. Synthesize response with LLM and citations
5. Return answer with confidence score and escalation flag

### Analytics

The analytics agent provides various endpoints:
- `/api/v1/analytics/summary` - High-level metrics (conversations, issues, agents, customers)
- `/api/v1/analytics/issues/distribution` - Top issues by occurrence
- `/api/v1/analytics/agents/performance` - Agent performance metrics
- `/api/v1/analytics/customers` - Customer list with conversation counts
- `/api/v1/analytics/customers/{id}/issues` - Customer issue history
- `/api/v1/analytics/resolution-time` - Resolution time statistics by issue type
- `/api/v1/analytics/escalation` - AI vs human resolution analytics with effort saved calculations

## Data Flow Example

### Complete Ingestion Flow

```
1. Client sends POST /api/v1/ingest
   ↓
2. Master Agent (LangGraph)
   - Creates correlation_id: "abc-123"
   - State: route → wait_response → complete
   - Publishes to pubsub: ingest.request
   ↓
3. Pub/Sub Service
   - Stores message in ingest.request queue
   - Message includes correlation_id
   ↓
4. Ingest Agent (polling)
   - Polls ingest.request every 100ms
   - Receives message with correlation_id
   ↓
5. Processing Pipeline
   a. PII Redaction
      - Regex patterns for email, phone, SSN, etc.
      - Redacts sensitive data
   
   b. LLM Extraction (Gemini)
      - Analyzes conversation
      - Extracts canonical issues
      - Extracts solutions with steps
      - Generates confidence scores
   
   c. Embedding Generation
      - Creates 768-dim vectors
      - For each issue and solution
   
   d. Neo4j Storage
      - MERGE Customer node
      - MERGE Agent node
      - CREATE Conversation node
      - CREATE Issue nodes with embeddings
      - CREATE Solution nodes with embeddings
      - CREATE relationships
   
   e. Vector Similarity Check
      - Searches existing issues
      - Merges if similarity > 0.85
   ↓
6. Response Publishing
   - Publishes to ingest.response
   - Includes correlation_id: "abc-123"
   ↓
7. Master Agent (polling)
   - Peeks ingest.response for correlation_id
   - Acknowledges message (removes from queue)
   - Returns result to client
```

### Complete Chat Flow

```
1. Client sends POST /api/v1/chat
   ↓
2. Master Agent (LangGraph)
   - Creates correlation_id: "xyz-789"
   - Publishes to chat.request
   ↓
3. Chat Agent (polling)
   - Receives query: "payment failing"
   ↓
4. Retrieval Pipeline
   a. Query Embedding
      - Generates 768-dim vector
   
   b. Vector Search (Neo4j)
      - Searches issue_embeddings index
      - Searches solution_embeddings index
      - Returns top 10 candidates
   
   c. Candidate Ranking
      - Similarity: 40%
      - Quality: 30%
      - Human review: 20%
      - Recency: 10%
      - Filters by threshold (0.7)
   
   d. Response Synthesis (Gemini)
      - Takes top 5 candidates
      - Generates response with citations
      - Calculates confidence
      - Determines escalation need
   
   e. Source References
      - Fetches conversation snippets
      - Builds source metadata
   ↓
5. Response Publishing
   - Publishes to chat.response
   - Includes correlation_id: "xyz-789"
   ↓
6. Master Agent returns to client
```

## Scaling & Performance

### Independent Scaling
Each agent scales independently based on its workload characteristics:

**Ingest Agent**:
- Processing time: 10-30 seconds per conversation
- Bottleneck: Gemini API calls (extraction + embeddings)
- Recommended: 2-4 instances for production
- Throughput: ~10-20 conversations/minute per instance

**Chat Agent**:
- Response time: 5-15 seconds per query
- Bottleneck: Vector search + Gemini synthesis
- Recommended: 5-10 instances for production
- Throughput: ~20-40 queries/minute per instance

**Master Agent**:
- Overhead: <100ms per request
- Non-blocking: Can handle 1000s of concurrent requests
- Recommended: 1-3 instances
- Throughput: Limited by worker agents, not master

**Pub/Sub**:
- Latency: <10ms per message
- In-memory: Very fast
- Recommended: 1-2 instances
- Throughput: 10,000+ messages/second

### Cost Optimization
Worker agents (ingest, chat) can scale to zero during low traffic periods, while the master agent should maintain at least one instance for fast response times. Each agent can be configured with different CPU and memory allocations based on its workload.

## Technology Stack

### Core Technologies
- **Python 3.11**: Async/await for concurrent processing
- **FastAPI**: High-performance async web framework
- **LangGraph**: State machine workflow orchestration
- **Neo4j**: Graph database with vector search
- **Google Gemini**: LLM for extraction and synthesis
- **Docker**: Containerization for each agent
- **Structlog**: Structured logging

### Key Libraries
- `neo4j` (5.14.1): Async Neo4j driver
- `google-generativeai` (0.3.1): Gemini API client
- `langgraph` (0.0.20): State machine workflows
- `httpx` (0.25.1): Async HTTP client
- `pydantic` (2.5.0): Data validation
- `uvicorn` (0.24.0): ASGI server

### Infrastructure
- **Google Cloud Run**: Serverless container platform
- **GCP Secret Manager**: Secure credential storage
- **Neo4j Aura**: Managed graph database
- **Docker Compose**: Local development orchestration

## Architecture Benefits

### ✅ Agentic Design
- **Autonomous Workers**: Each agent operates independently with its own lifecycle
- **State Machine Orchestration**: LangGraph manages complex workflows
- **Asynchronous Communication**: Non-blocking pub/sub messaging
- **Self-Contained Intelligence**: Each agent has decision-making logic

### ✅ Scalability
- **Independent Scaling**: Scale each agent based on its workload
- **Horizontal Scaling**: Add more instances of any agent
- **Scale to Zero**: Reduce costs during low traffic
- **No Bottlenecks**: Master doesn't block on worker processing

### ✅ Reliability
- **Fault Isolation**: One agent failure doesn't affect others
- **Graceful Degradation**: Services continue with reduced functionality
- **Retry Logic**: Automatic retries for transient failures
- **Health Checks**: Continuous monitoring of each service

### ✅ Maintainability
- **Separation of Concerns**: Each agent has a single responsibility
- **Shared Business Logic**: DRY principle with core/services modules
- **Easy Testing**: Test agents in isolation
- **Clear Interfaces**: Well-defined pub/sub contracts

### ✅ Cost Efficiency
- **Pay Per Use**: Cloud Run charges only for actual usage
- **Resource Optimization**: Right-size each agent independently
- **Auto-Scaling**: Automatic scaling based on demand
- **Efficient Resource Allocation**: CPU/memory tuned per agent

### ✅ Developer Experience
- **Local Development**: Docker Compose for full stack
- **Hot Reload**: Fast iteration during development
- **Structured Logging**: Easy debugging with correlation IDs
- **Type Safety**: Pydantic models for all data structures

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTERNET                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  Load Balancer │
                    └────────┬───────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Master Agent   │ ◄── Cloud Run Service
                    │ (0-5 instances)│     • Public endpoint
                    └────────┬───────┘     • LangGraph orchestration
                             │             • Auto-scaling
                             ▼
                    ┌────────────────┐
                    │   Pub/Sub      │ ◄── Cloud Run Service
                    │ (1-3 instances)│     • Internal only
                    └────┬───────┬───┘     • Message routing
                         │       │         • In-memory queues
           ┌─────────────┘       └─────────────┐
           ▼                                   ▼
    ┌──────────────┐                   ┌──────────────┐
    │ Ingest Agent │                   │  Chat Agent  │
    │ (0-10 inst.) │                   │ (0-20 inst.) │
    └──────┬───────┘                   └──────┬───────┘
           │                                   │
           │  ┌────────────────┐              │
           └──┤ Analytics Agent│──────────────┘
              │  (0-3 inst.)   │
              └────────┬───────┘
                       │
                       ▼
              ┌────────────────┐
              │    Neo4j Aura  │ ◄── Managed Database
              │   (Cloud)      │     • Vector search
              └────────────────┘     • Graph queries
                       │
                       ▼
              ┌────────────────┐
              │ GCP Secrets    │ ◄── Secret Manager
              │  Manager       │     • Credentials
              └────────────────┘     • API keys
```

---

**Production-ready agentic system for intelligent customer support** 🚀


## Testing & Troubleshooting

### Health Checks
Each service exposes a `/health` endpoint that reports service status and database connectivity. The master agent also proxies analytics requests.

### Common Issues

**Ingest agent not processing messages**:
- Verify Neo4j connection via health endpoint
- Check GEMINI_API_KEY is configured
- Ensure pub/sub service is running
- Review agent logs for errors

**Chat agent returns low confidence**:
- Ensure conversations are ingested first
- Verify vector indexes exist in Neo4j (requires Neo4j 5.11+)
- Check that embeddings are generated on Issue/Solution nodes
- System works without vector indexes but won't deduplicate similar issues

**Master agent timeout**:
- Default timeout is 300 seconds
- Check worker agent logs for processing errors
- Verify pub/sub message delivery using correlation_id
- Ensure worker agents are polling their topics

**Vector search not working**:
- Requires Neo4j 5.11+ for vector index support
- Check if indexes were created during schema initialization
- System gracefully degrades without vector search

### Debugging
Enable detailed logging by setting LOG_LEVEL=DEBUG. All services use structured logging with correlation IDs for request tracing across the distributed system. Use docker-compose logs to view agent output.


