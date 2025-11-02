# Customer Conversation Knowledge Engine

A production-ready, containerized microservice that converts historical customer-agent chat logs into a searchable knowledge base using AI. The system extracts canonical issues and solutions, stores them in Neo4j with embeddings, and provides intelligent responses to customer queries.

## Features

- **Intelligent Ingestion**: Converts chat logs into canonical issues/solutions using Gemini LLM
- **PII Protection**: Automatically redacts sensitive information
- **Vector Search**: Semantic similarity search using embeddings
- **Graph Storage**: Neo4j for relationships and provenance tracking
- **AI Responses**: LLM-synthesized answers with source citations
- **Human Review**: Quality control workflow for continuous improvement
- **Containerized**: Full Docker setup for easy deployment

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Setup

1. **Clone and configure**:
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env and add your Gemini API key
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

2. **Start services**:
   ```bash
   # Use the setup script (recommended)
   ./scripts/docker_setup.sh    # Linux/Mac
   # or
   scripts\docker_setup.bat     # Windows
   
   # Or manually
   docker-compose up -d
   ```

3. **Wait for services** (Neo4j takes ~30 seconds to initialize):
   ```bash
   # Check logs
   docker-compose logs -f
   
   # Test database connection
   python scripts/db_management.py check
   ```

4. **Test with sample data**:
   ```bash
   python test_data.py
   ```

### API Endpoints

**Health Check**:
```bash
curl http://localhost:8000/health
```

**Ingest Conversations**:
```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "conversations": [
      {
        "conversation_id": "conv_001",
        "customer_id": "customer_123", 
        "agent_id": "agent_456",
        "messages": [
          {
            "role": "customer",
            "content": "I cannot log into my account"
          },
          {
            "role": "agent", 
            "content": "Let me help you reset your password..."
          }
        ]
      }
    ]
  }'
```

**Chat Query**:
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I cannot log into my account",
    "customer_id": "customer_123"
  }'
```

**Knowledge Stats**:
```bash
curl http://localhost:8000/api/v1/knowledge/stats
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │     Neo4j       │    │   Gemini API    │
│   Service       │◄──►│   Database      │    │   (External)    │
│                 │    │                 │    │                 │
│ • Ingestion     │    │ • Graph Storage │    │ • LLM Tasks     │
│ • Chat API      │    │ • Vector Index  │    │ • Embeddings    │
│ • PII Redaction │    │ • Relationships │    │ • Synthesis     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Data Flow

### Ingestion Pipeline
1. **Input**: JSON conversations with customer/agent messages
2. **PII Redaction**: Remove sensitive information
3. **LLM Processing**: Extract canonical issues/solutions
4. **Embedding Generation**: Create vector representations
5. **Deduplication**: Merge similar existing issues
6. **Graph Storage**: Store with full provenance in Neo4j

### Query Pipeline  
1. **Query Input**: Customer question + context
2. **Vector Search**: Find similar issues/solutions
3. **Graph Expansion**: Retrieve related context
4. **Ranking**: Score by similarity + quality + human review
5. **LLM Synthesis**: Generate cited response
6. **Response**: Return answer with sources and confidence

## Configuration

Key environment variables in `.env`:

```bash
# Required
GEMINI_API_KEY=your_api_key

# Optional (defaults provided)
NEO4J_URI=bolt://neo4j:7687
SIMILARITY_THRESHOLD=0.85
CONFIDENCE_THRESHOLD=0.7
MAX_RETRIEVAL_RESULTS=10
```

## Development

**View logs**:
```bash
docker-compose logs -f api
docker-compose logs -f neo4j
```

**Access Neo4j Browser**:
- URL: http://localhost:7474
- Username: neo4j
- Password: password123

**API Documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Production Deployment

For production:

1. **Security**:
   - Change default Neo4j password
   - Set strong SECRET_KEY
   - Enable TLS/SSL
   - Add authentication middleware

2. **Scaling**:
   - Use managed Neo4j (Neo4j Aura)
   - Deploy API with load balancer
   - Add Redis for caching
   - Implement rate limiting

3. **Monitoring**:
   - Add structured logging
   - Implement health checks
   - Monitor embedding costs
   - Track response quality metrics

## Data Persistence

The system uses Docker named volumes for Neo4j data persistence:

- `neo4j_data`: Database files and indexes
- `neo4j_logs`: Database logs
- `neo4j_import`: Import directory
- `neo4j_plugins`: Plugin files

**Data Management**:
```bash
# Check database status
python scripts/db_management.py info

# Initialize schema (if needed)
python scripts/db_management.py init

# Clear all data (caution!)
python scripts/db_management.py clear
```

**Backup/Restore**:
```bash
# Backup volumes
docker run --rm -v neo4j_data:/data -v $(pwd):/backup alpine tar czf /backup/neo4j_backup.tar.gz /data

# Restore volumes
docker run --rm -v neo4j_data:/data -v $(pwd):/backup alpine tar xzf /backup/neo4j_backup.tar.gz -C /
```

## Troubleshooting

**Services won't start**:
- Check Docker is running
- Verify ports 7474, 7687, 8000 are available
- Check logs: `docker-compose logs`
- Use setup script: `./scripts/docker_setup.sh`

**Database connection issues**:
- Wait for Neo4j health check to pass
- Test connection: `python scripts/db_management.py check`
- Check Neo4j logs: `docker-compose logs neo4j`

**Data persistence problems**:
- Verify named volumes exist: `docker volume ls`
- Check volume mounts in docker-compose.yml
- Ensure proper shutdown: `docker-compose down` (not `docker-compose down -v`)

**Ingestion fails**:
- Verify Gemini API key is valid
- Check Neo4j connection
- Review conversation format

**No search results**:
- Ensure data was ingested successfully
- Check similarity thresholds
- Verify embeddings were generated

**Low response quality**:
- Review and approve solutions via human workflow
- Adjust confidence thresholds
- Add more training conversations