# Customer Conversation Knowledge Engine

An AI-powered system that transforms historical customer-agent conversations into a searchable knowledge base. Built with FastAPI, Neo4j, and Google Gemini, this production-ready microservice extracts canonical issues and solutions from chat logs, enabling intelligent responses to customer queries with full provenance tracking.

## Overview

This system ingests customer support conversations, uses LLMs to extract and canonicalize issues/solutions, stores them in a graph database with vector embeddings, and provides an API for semantic search and AI-synthesized responses.

**Key Capabilities:**
- Intelligent conversation ingestion with PII redaction
- Semantic search using vector embeddings
- Graph-based knowledge storage with relationships
- LLM-synthesized responses with source citations
- Human review workflow for quality control
- Full Docker containerization for easy deployment
- Terraform infrastructure as code for GCP deployment

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
 
## Project Structure

```
.
├── services/              # Main application code
│   ├── api/              # FastAPI routes and endpoints
│   ├── core/             # Core business logic and database
│   ├── models/           # Pydantic models and schemas
│   ├── services/         # Service layer (LLM, embeddings, etc.)
│   ├── main.py           # Application entry point
│   ├── requirements.txt  # Python dependencies
│   ├── Dockerfile        # Container image definition
│   └── docker-compose.yml # Local development setup
├── terraform/            # Infrastructure as code
│   ├── main.tf          # Main Terraform configuration
│   ├── variables.tf     # Variable definitions
│   └── terraform.tfvars # Variable values (gitignored)
└── README.md            # This file
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Configure environment**:
   ```bash
   cd services
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

3. **Start services with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

4. **Wait for services to initialize** (Neo4j takes ~30 seconds):
   ```bash
   docker-compose logs -f
   ```

5. **Verify the setup**:
   ```bash
   curl http://localhost:8000/health
   ```

### API Usage

**Health Check**:
```bash
curl http://localhost:8000/health
```

**Ingest Conversations**:
```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d @sample_ingest_data.json
```

**Query the Knowledge Base**:
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I reset my password?",
    "customer_id": "customer_123"
  }'
```

**Get Knowledge Stats**:
```bash
curl http://localhost:8000/api/v1/knowledge/stats
```

## Development

### Running Locally Without Docker

1. **Install dependencies**:
   ```bash
   cd services
   pip install -r requirements.txt
   ```

2. **Start Neo4j** (via Docker or local installation)

3. **Run the application**:
   ```bash
   python main.py
   ```

### API Documentation

Once running, access interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Neo4j Browser

Access the Neo4j browser interface:
- URL: http://localhost:7474
- Username: neo4j
- Password: (check your .env file)

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f neo4j
```

## Configuration

Key environment variables (in `services/.env`):

```bash
# Required
GEMINI_API_KEY=your_api_key_here

# Neo4j Configuration
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# LLM Configuration
GEMINI_MODEL_NAME=gemini-1.5-flash
GEMINI_EMBEDDING_MODEL=models/embedding-001

# Application Settings
SIMILARITY_THRESHOLD=0.85
CONFIDENCE_THRESHOLD=0.7
MAX_RETRIEVAL_RESULTS=10
CHUNK_SIZE=1000
SECRET_KEY=your-secret-key-here
```

## Production Deployment

### Deploy to Google Cloud Run with Terraform

This project includes Terraform configuration to deploy the Docker image to Cloud Run with all necessary infrastructure.

**Prerequisites**:
- GCP account with billing enabled
- `gcloud` CLI installed and authenticated
- Terraform installed
- Neo4j Aura instance or hosted Neo4j (get free tier at [neo4j.com/cloud/aura](https://neo4j.com/cloud/aura))
- Gemini API key

**Deployment Steps**:

1. **Enable required GCP APIs**:
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable artifactregistry.googleapis.com
   ```

2. **Build and push Docker image**:
   ```bash
   cd services
   
   # Build the image
   docker build -t knowledge-engine:latest .
   
   # Tag for Artifact Registry
   docker tag knowledge-engine:latest \
     us-central1-docker.pkg.dev/YOUR_PROJECT_ID/dataalchemist/knowledge-engine:latest
   
   # Configure Docker auth
   gcloud auth configure-docker us-central1-docker.pkg.dev
   
   # Push to registry
   docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/dataalchemist/knowledge-engine:latest
   ```

3. **Configure Terraform**:
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values:
   # - project_id: Your GCP project ID
   # - neo4j_uri: Your Neo4j Aura connection string
   # - neo4j_password: Your Neo4j password
   # - gemini_api_key: Your Gemini API key
   # - app_secret_key: Generate a random secret key
   ```

4. **Deploy infrastructure**:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

5. **Get your Cloud Run URL**:
   ```bash
   terraform output cloud_run_url
   ```

The output will show your public Cloud Run URL (e.g., `https://knowledge-engine-api-xxxxx-uc.a.run.app`). You can immediately start using the API at this endpoint.

**Test the deployment**:
```bash
# Get the URL
CLOUD_RUN_URL=$(terraform output -raw cloud_run_url)

# Health check
curl $CLOUD_RUN_URL/health

# Ingest data
curl -X POST $CLOUD_RUN_URL/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d @../sample_data.json
```

### Production Checklist

- [ ] Use Neo4j Aura (managed service) for production database
- [ ] Generate strong random SECRET_KEY
- [ ] Review Cloud Run scaling settings (min/max instances)
- [ ] Set up Cloud Monitoring and alerting
- [ ] Configure Cloud Logging for centralized logs
- [ ] Add authentication if needed (API keys, OAuth, etc.)
- [ ] Configure rate limiting via Cloud Armor
- [ ] Set up CI/CD pipeline (GitHub Actions included)
- [ ] Review IAM permissions and follow least privilege
- [ ] Enable Cloud Run audit logs

## Data Pipeline

### Ingestion Flow
1. Receive JSON conversations with customer/agent messages
2. Redact PII (personally identifiable information)
3. Use LLM to extract canonical issues and solutions
4. Generate vector embeddings
5. Check for duplicates and merge similar issues
6. Store in Neo4j with full provenance

### Query Flow
1. Receive customer query
2. Generate query embedding
3. Perform vector similarity search
4. Retrieve related context from graph
5. Rank results by similarity, quality, and human review
6. Synthesize response using LLM
7. Return answer with source citations and confidence score

## Troubleshooting

**Services won't start**:
- Verify Docker is running
- Check ports 7474, 7687, 8000 are available
- Review logs: `docker-compose logs`

**Database connection issues**:
- Wait for Neo4j to fully initialize (~30 seconds)
- Check Neo4j logs: `docker-compose logs neo4j`
- Verify credentials in .env file

**Ingestion fails**:
- Verify Gemini API key is valid and has quota
- Check Neo4j connection
- Review conversation JSON format

**No search results**:
- Ensure data was ingested successfully
- Check similarity thresholds in configuration
- Verify embeddings were generated

## Technology Stack

- **API Framework**: FastAPI
- **Database**: Neo4j (graph database with vector search)
- **LLM**: Google Gemini (text generation and embeddings)
- **Containerization**: Docker & Docker Compose
- **Infrastructure**: Terraform (GCP)
- **Language**: Python 3.11+

## License

See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For detailed service documentation, see [services/README.md](services/README.md).
