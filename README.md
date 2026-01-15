# Agentic Customer Support System

An AI-powered customer support system that learns from past conversations and automatically answers questions. Think of it as a smart assistant that gets smarter over time by analyzing how your team solves problems.

## What Does It Do?

**For Support Teams:**
- Automatically answers 40-60% of common questions
- Works 24/7 without breaks
- Learns from every conversation you feed it
- Only escalates to humans when it's not confident

**For Customers:**
- Instant answers backed by real solutions
- Shows sources (like "this worked for 5 other customers")
- Natural conversation, not robotic responses
- Falls back to human support when needed

## How It Works

### Ingestion Pipeline

```


Raw Conversation
        ↓
   ┌────────────────────┐
   │  1. PII Redaction  │  Email → [EMAIL], Phone → [PHONE]
   └─────────┬──────────┘
             ↓
   ┌────────────────────┐
   │ 2. LLM Extraction  │  "Can't login" → "Authentication failure"
   └─────────┬──────────┘
             ↓
   ┌────────────────────┐
   │ 3. Embedding Gen   │  Text → 768-dim vector
   └─────────┬──────────┘
             ↓
   ┌────────────────────┐
   │ 4. Duplicate Check │  Similarity > 85%? Merge : Create
   └─────────┬──────────┘
             ↓
   ┌────────────────────┐
   │ 5. Store in Neo4j  │  Save with relationships
   └────────────────────┘
```

### Query Pipeline

```
Customer Question: "Password reset not working"
        ↓
   ┌────────────────────┐
   │ 1. Generate Vector │  Question → embedding
   └─────────┬──────────┘
             ↓
   ┌────────────────────┐
   │ 2. Vector Search   │  Find top 10 similar issues
   └─────────┬──────────┘
             ↓
   ┌────────────────────┐
   │ 3. Rank Results    │  Similarity (40%) + Quality (30%)
   │                    │  + Human Review (20%) + Recency (10%)
   └─────────┬──────────┘
             ↓
   ┌────────────────────┐
   │ 4. LLM Synthesis   │  Generate natural answer
   └─────────┬──────────┘
             ↓
   ┌────────────────────┐
   │ 5. Confidence Check│  >70%? Return : Escalate
   └─────────┬──────────┘
             ↓
    "Try /forgot-password..."
    Confidence: 92%
    [Sources: 3 similar tickets]
```

Think of it as three smart workers talking to each other:

1. **Ingest Worker** - Reads old support conversations, removes sensitive info (emails, phone numbers), and extracts the core problem and solution
2. **Chat Worker** - Answers customer questions by finding similar past issues and generating helpful responses
3. **Analytics Worker** - Tracks what's working, what's not, and how much time you're saving

They coordinate through a **Master Agent** that routes requests and makes sure everything runs smoothly.

## Tech Stack

- **Python + FastAPI** for the backend
- **Neo4j** for storing conversations and relationships (why customers contact you, what solved their issues)
- **Google Gemini** for understanding text and generating responses
- **LangGraph** for orchestrating the workflow
- **Docker** for easy deployment

## Quick Start

### You'll Need
- Docker installed
- A Neo4j database (free tier works)
- Google Gemini API key

### Get It Running

1. **Set up your environment**
```bash
cd services
cp .env.example .env
# Add your Neo4j and Gemini credentials
```

2. **Start everything**
```bash
docker-compose up
```

3. **Test it out**
```bash
# Feed it some conversations
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d @sample_conversations.json

# Ask a question
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I reset my password?"}'
```

The system will:
- Redact any sensitive info
- Extract the real problem and solution
- Store it in the knowledge base
- Use it to answer future questions

## Architecture

### High-Level System Flow

```
┌─────────────┐
│   Client    │
│  (Web/API)  │
└──────┬──────┘
       │ HTTP Request
       ▼
┌─────────────────────────────────────┐
│       Master Agent (Port 8000)      │
│  • Routes requests                  │
│  • Manages workflow                 │
│  • Tracks correlation IDs           │
└──────┬──────────────────────────────┘
       │ Publish message
       ▼
┌─────────────────────────────────────┐
│     Message Bus (Port 8001)         │
│  • Async communication              │
│  • Request/response queues          │
└──────┬──────────────────────────────┘
       │ Workers poll for tasks
       ├─────────┬───────────┐
       ▼         ▼           ▼          
   ┌────────┐ ┌──────┐ ┌──────────┐
   │ Ingest │ │ Chat │ │Analytics │
   │ Agent  │ │Agent │ │  Agent   │
   │ :8002  │ │:8003 │ │  :8004   │
   └───┬────┘ └──┬───┘ └────┬─────┘
       │         │          │
       └─────────┴──────────┘
                 │
                 ▼
   ┌──────────────────────────┐
   │  Neo4j + Gemini API      │
   │  • Graph database        │
   │  • Vector embeddings     │
   │  • LLM processing        │
   └──────────────────────────┘
```

### Request Flow Example

```
1. Customer asks: "How do I reset my password?"
   │
   ▼
2. Master Agent creates correlation ID: "abc-123"
   │
   ▼
3. Publishes to chat.request queue
   │
   ▼
4. Chat Agent polls and picks up message
   │
   ├─> Generates query embedding
   ├─> Searches Neo4j for similar issues
   ├─> Ranks by similarity + quality
   ├─> Asks Gemini to synthesize answer
   │
   ▼
5. Publishes response to chat.response queue
   │
   ▼
6. Master Agent retrieves response (filters by "abc-123")
   │
   ▼
7. Returns to customer:
   "Try /forgot-password. If that fails, clear your 
    browser cache. [Source: 8 similar tickets]"
    Confidence: 92%
```

### Data Model

```
┌─────────────┐
│  Customer   │
└──────┬──────┘
       │ HAS
       ▼
┌─────────────────┐
│  Conversation   │◄─── HANDLED_BY ───┐
│  • Raw text     │                   │
│  • Timestamp    │              ┌────┴────┐
└──────┬──────────┘              │  Agent  │
       │ CONTAINS                └─────────┘
       ├─────────────┬──────────┐
       ▼             ▼          ▼
┌─────────┐   ┌──────────┐  ┌──────────┐
│  Issue  │   │ Solution │  │   Tags   │
│• Vector │   │ • Vector │  └──────────┘     
│• Text   │   │ • Steps  │            
└─────────┘   └──────────┘  
     │
     └─── SIMILAR_TO ───┐
                        │
                   (finds duplicates)
```

### Why This Design?

**Independent Workers:** Each component can scale separately. Need more chat capacity? Spin up more chat workers without touching anything else.

**Fault Tolerant:** If one worker crashes, the others keep running. Your system degrades gracefully instead of dying completely.

**Async Communication:** Workers don't wait for each other. They pick up tasks when ready, process them, and move on.

## Project Structure

```
services/
  ├── agents/           # Independent workers
  │   ├── master/       # Routes requests, manages workflow
  │   ├── ingest/       # Processes conversations
  │   ├── chat/         # Answers questions
  │   └── analytics/    # Tracks metrics
  ├── core/             # Shared code (database, LLM, config)
  ├── models/           # Data structures
  └── docker-compose.yml

terraform/              # Deploy to Google Cloud
  ├── agentic_system.tf # Cloud Run setup
  ├── secrets.tf        # Secure credential storage
  └── README.md         # Deployment guide
```

## Real-World Example

**Before:** Customer asks "I can't log in"
- Goes to support queue
- Human agent spends 5 minutes finding solution
- Repeats 50 times per day

**After:** Same question
- System finds 10 similar past issues in <1 second
- Synthesizes answer: "Try resetting your password at /forgot. If that fails, clear your browser cache."
- Shows sources: "Worked for 8/10 customers"
- Confidence: 92%

**Result:** 50 tickets × 5 minutes = 250 minutes saved daily

## Key Features

**Smart Processing:**
- Automatically removes PII (emails, phone numbers, credit cards)
- Finds duplicate issues to keep knowledge base clean
- Ranks answers by similarity + quality + recency

**Production Ready:**
- Health checks on all services
- Structured logging with request tracking
- Secrets stored securely (never in code)
- Auto-scales based on traffic

**Analytics:**
- How many questions AI answered vs. escalated
- Resolution time trends
- Most common issues
- ROI calculation (time saved)

## Deploy to Production

**Local Development:**
```bash
docker-compose up  # Everything runs on your machine
```

**Google Cloud:**
```bash
cd terraform
terraform init
terraform apply  # Provisions Cloud Run, Secret Manager, etc.
```

Cloud Run scales automatically from 1-10 instances based on traffic. Costs ~$5-10/month for dev, $100-200/month for production (plus Neo4j/Gemini API).

## Performance

### Throughput by Agent

```
Agent          Requests/min    Bottleneck
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Master         1000+           (orchestration only)
Ingest         10-20           LLM API calls
Chat           20-40           Vector search + LLM
Analytics      100+            Database queries
```

### Typical Response Times

```
Operation              Time         What's Happening
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Master routing         <100ms       Create correlation ID
Vector search          <100ms       Find similar issues
Graph traversal        <50ms        Get relationships
LLM synthesis          3-10s        Generate answer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total query time       5-15s        End-to-end
Total ingestion time   10-30s       Per conversation
```

### Scaling Characteristics

```
Load Level      Auto-scaling Response
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Low traffic     1 instance (scales to 0)
Normal          2-3 instances
High traffic    Up to 10 instances
Peak burst      Request queuing

Each instance: 2 CPU, 4GB RAM
```

## When to Use This

✅ **Good fit if you:**
- Have repetitive support questions
- Want to reduce support load
- Need 24/7 coverage
- Have historical conversation data

❌ **Not ideal if you:**
- Need real-time (<1 second) responses
- Have highly regulated data (medical, financial) without proper compliance setup
- Want 100% accuracy (it's AI, not magic - expect 70-90% confidence on most answers)

## Contributing

Want to add features? Some ideas:
- Multi-language support
- Human review dashboard
- Response caching for common questions
- Fine-tune embeddings for your domain

## Questions?

Check the detailed docs:
- `services/README.md` - Deep dive on architecture
- `terraform/README.md` - Production deployment guide

Or just try it out - the quick start takes 5 minutes.