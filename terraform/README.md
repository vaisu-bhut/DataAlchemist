# Terraform Infrastructure for Agentic System

Infrastructure as Code for deploying the multi-agent customer support system to Google Cloud Platform. This configuration provisions all required cloud resources including Cloud Run services, Secret Manager, Artifact Registry, and IAM permissions.

## Infrastructure Overview

This Terraform configuration deploys a unified container architecture where all agents run within a single Cloud Run service. This approach optimizes for cost, simplicity, and inter-service communication speed while maintaining the logical separation of agent responsibilities.

### Deployment Model

**Single Container Architecture**:
- All five services (Master, Pub/Sub, Ingest, Chat, Analytics) run in one Cloud Run service
- Managed by Supervisord process manager inside the container
- Services communicate via localhost (no network latency)
- Shared resource pool (CPU/memory) across all agents
- Single deployment unit for simplified management

**Alternative**: For production systems requiring independent scaling, each agent can be deployed as a separate Cloud Run service. This Terraform configuration uses the unified approach for cost efficiency and simplicity.

## File Structure

**provider.tf** - GCP provider configuration and project settings

**variables.tf** - Input variables for configuration (project ID, region, credentials, thresholds)

**terraform.tfvars** - Your actual values (not in git, created from example)

**versions.tf** - Terraform and provider version constraints

**apis.tf** - Enables required GCP APIs (Cloud Run, Secret Manager, Artifact Registry)

**artifact_registry.tf** - Docker container registry for storing images

**secrets.tf** - Secret Manager secrets for credentials and configuration

**agentic_system.tf** - Main Cloud Run service definition with all agents

**outputs.tf** - Exported values (service URL, endpoints, usage instructions)

## Cloud Architecture

### Deployed Infrastructure

```
┌─────────────────────────────────────────────────────────────────┐
│                      Google Cloud Platform                       │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              Cloud Run Service (Public)                 │    │
│  │                  agentic-system                         │    │
│  │                                                          │    │
│  │  ┌──────────────────────────────────────────────┐      │    │
│  │  │         Supervisord Process Manager          │      │    │
│  │  │  (Manages all services in one container)     │      │    │
│  │  └──────────────────────────────────────────────┘      │    │
│  │                                                          │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │    │
│  │  │ Pub/Sub  │  │  Master  │  │Analytics │             │    │
│  │  │  :8001   │◄─┤  :8000   │◄─┤  :8004   │             │    │
│  │  └──────────┘  └──────────┘  └──────────┘             │    │
│  │                      ▲                                  │    │
│  │  ┌──────────┐  ┌────┴─────┐                           │    │
│  │  │  Ingest  │  │   Chat   │                           │    │
│  │  │  :8002   │  │  :8003   │                           │    │
│  │  └──────────┘  └──────────┘                           │    │
│  │                                                          │    │
│  │  Resources: 2 CPU, 4GB RAM (shared)                    │    │
│  │  Scaling: 1-10 instances                               │    │
│  │  Timeout: 300s                                         │    │
│  └────────────────────────────────────────────────────────┘    │
│                           │                                     │
│                           │ Fetches secrets at startup          │
│                           ▼                                     │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              Secret Manager (Private)                   │    │
│  │                                                          │    │
│  │  ┌──────────────────────────────────────────┐          │    │
│  │  │  database-credentials (JSON)             │          │    │
│  │  │  - neo4j_uri                             │          │    │
│  │  │  - neo4j_user                            │          │    │
│  │  │  - neo4j_password                        │          │    │
│  │  └──────────────────────────────────────────┘          │    │
│  │                                                          │    │
│  │  ┌──────────────────────────────────────────┐          │    │
│  │  │  api-keys (JSON)                         │          │    │
│  │  │  - gemini_api_key                        │          │    │
│  │  │  - gemini_model_name                     │          │    │
│  │  │  - gemini_embedding_model                │          │    │
│  │  │  - app_secret_key                        │          │    │
│  │  │  - chunk_size, thresholds, etc.          │          │    │
│  │  └──────────────────────────────────────────┘          │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │         Artifact Registry (Private)                     │    │
│  │                                                          │    │
│  │  Docker Repository: agentic-system                      │    │
│  │  - agentic-system:latest                               │    │
│  │  - agentic-system:v1.0.0                               │    │
│  │  - agentic-system:commit-abc123                        │    │
│  └────────────────────────────────────────────────────────┘    │
│                           ▲                                     │
│                           │ Push images                         │
│                           │                                     │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                 GitHub Actions                         │    │
│  │  (CI/CD Pipeline - builds and pushes images)           │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ Connects to
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                             │
│                                                                  │
│  ┌──────────────────────┐      ┌──────────────────────┐        │
│  │   Neo4j Aura         │      │  Google Gemini API   │        │
│  │   (Graph Database)   │      │  (LLM Service)       │        │
│  └──────────────────────┘      └──────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Benefits

**Unified Container Approach**:
- Single deployment unit simplifies management
- Localhost communication eliminates network latency
- Shared resource pool reduces costs
- Faster cold starts (one container vs multiple)
- Simplified monitoring and logging

**Trade-offs**:
- All agents share CPU/memory resources
- Cannot scale agents independently
- One agent failure can affect others
- Suitable for small-to-medium workloads

**When to Use Separate Services**:
- High traffic requiring independent scaling
- Different resource requirements per agent
- Need for fault isolation
- Production systems with strict SLAs

## Deployment Process

### Prerequisites

**Google Cloud Platform**:
- GCP project with billing enabled
- Owner or Editor role on the project
- gcloud CLI installed and authenticated

**External Services**:
- Neo4j Aura database (or self-hosted Neo4j 5.11+)
- Google Gemini API key

**Local Tools**:
- Terraform 1.0+ installed
- Docker (for building images)
- Git (for version control)

### Configuration Steps

**1. Enable GCP APIs**

The terraform configuration automatically enables required APIs:
- Cloud Run API (run.googleapis.com)
- Secret Manager API (secretmanager.googleapis.com)
- Artifact Registry API (artifactregistry.googleapis.com)

**2. Configure Variables**

Create `terraform.tfvars` from the example file and provide:

**Project Settings**:
- GCP project ID
- Deployment region (default: us-central1)
- Service account email for Cloud Run

**Database Credentials**:
- Neo4j connection URI (neo4j+s://...)
- Neo4j username (default: neo4j)
- Neo4j password

**API Keys**:
- Gemini API key
- Gemini model name (default: gemini-2.0-flash-exp)
- Gemini embedding model (default: text-embedding-004)

**Application Settings**:
- Secret key for encryption (generate random string)
- Chunk size for text processing (default: 2000)
- Similarity threshold (default: 0.85)
- Confidence threshold (default: 0.7)
- Max retrieval results (default: 10)

**3. Initialize Terraform**

Run `terraform init` to download provider plugins and initialize the backend. This creates a `.terraform` directory with provider binaries.

**4. Review Plan**

Run `terraform plan` to preview all resources that will be created:
- Artifact Registry repository
- Two Secret Manager secrets (database-credentials, api-keys)
- IAM bindings for secret access
- Cloud Run service with container configuration

**5. Apply Configuration**

Run `terraform apply` to create all resources. Terraform will:
- Enable required APIs
- Create Artifact Registry repository
- Store credentials in Secret Manager
- Grant IAM permissions
- Deploy Cloud Run service
- Configure auto-scaling and networking

**6. Verify Deployment**

After successful apply, Terraform outputs:
- Service URL (public endpoint)
- Artifact Registry repository URL
- Service name and location
- Usage instructions

## CI/CD Integration

### Build and Deploy Pipeline

**Image Building**:
- GitHub Actions or Cloud Build builds the Docker image
- Image is tagged with version/commit hash
- Image is pushed to Artifact Registry
- Terraform references the image in Cloud Run configuration

**Deployment Flow**:
1. Developer pushes code to repository
2. CI/CD pipeline builds Docker image
3. Image is pushed to Artifact Registry with tags
4. Run `terraform apply` to deploy new image
5. Cloud Run pulls latest image and creates new revision
6. Traffic is automatically routed to new revision

**Separation of Concerns**:
- CI/CD handles image building and registry push
- Terraform manages infrastructure and service configuration
- Cloud Run handles container orchestration and scaling

### Image Tagging Strategy

**Recommended Tags**:
- `latest` - Most recent build (used by Terraform)
- `v1.0.0` - Semantic version tags
- `commit-abc123` - Git commit hash
- `pr-42` - Pull request builds

**Terraform Configuration**:
The Cloud Run service references `latest` tag by default. For production, consider using specific version tags for reproducible deployments.

## Resource Details

### Cloud Run Service Configuration

**Service Specifications**:
- Service name: `agentic-system`
- Public endpoint with HTTPS
- Exposed port: 8000 (Master Agent API)
- Internal ports: 8001 (Pub/Sub), 8002 (Ingest), 8003 (Chat), 8004 (Analytics)
- All services communicate via localhost within container

**Resource Allocation**:
- CPU: 2 vCPUs (shared across all agents)
- Memory: 4GB RAM (shared across all agents)
- Timeout: 300 seconds (5 minutes for LLM processing)
- Concurrency: Default (80 requests per instance)

**Auto-Scaling Configuration**:
- Minimum instances: 1 (always warm, no cold starts)
- Maximum instances: 10 (scales based on traffic)
- CPU throttling: Enabled (reduces costs during idle)
- Scale-down delay: Default (gradual scale-down)

**Network Configuration**:
- Public ingress (accessible from internet)
- HTTPS only (automatic SSL certificate)
- IAM authentication: Disabled (public access)
- VPC connector: Not configured (uses default networking)

### Secret Manager

**database-credentials Secret**:
- Stores Neo4j connection details as JSON
- Fields: neo4j_uri, neo4j_user, neo4j_password
- Automatic replication across regions
- Versioned (can rollback to previous values)

**api-keys Secret**:
- Stores API keys and application configuration as JSON
- Fields: gemini_api_key, model names, thresholds, chunk size
- Automatic replication across regions
- Versioned (can rollback to previous values)

**IAM Permissions**:
- Cloud Run service account has `secretAccessor` role
- Secrets are mounted as environment variables at runtime
- No secrets stored in container images or Terraform state

### Artifact Registry

**Repository Configuration**:
- Format: Docker
- Location: Same region as Cloud Run service
- Repository name: `agentic-system`
- Access: Private (requires authentication)
- Cleanup policy: Not configured (manual cleanup)

**Image Storage**:
- Stores all versions of the agentic-system image
- Tagged with version numbers and commit hashes
- Cloud Run pulls images during deployment
- Images are cached for faster deployments

## State Management

### Destroying Infrastructure

Running `terraform destroy` removes all managed resources:
- Cloud Run service (stops all running instances)
- Secret Manager secrets (marks for deletion)
- Artifact Registry repository (deletes all images)
- IAM bindings (removes permissions)

**What's Not Deleted**:
- GCP project
- Enabled APIs (remain enabled)
- Service accounts (if created outside Terraform)
- Neo4j database (external service)
- Docker images in other registries

**Deletion Protection**:
Secret Manager secrets have a default deletion delay (30 days). They can be recovered during this period or permanently deleted immediately.

## Monitoring and Observability

### Cloud Logging

**Log Collection**:
All container output (stdout/stderr) is automatically collected by Cloud Logging. Each service within the container logs with structured JSON format including correlation IDs for request tracing.

**Log Filtering**:
Filter logs by service name, severity level, or correlation ID. Use the Cloud Console Logs Explorer or gcloud CLI for querying.

**Log Retention**:
Default retention is 30 days. Configure log sinks to export logs to Cloud Storage or BigQuery for long-term retention.

### Cloud Monitoring

**Automatic Metrics**:
Cloud Run automatically collects metrics:
- Request count and latency
- Container CPU and memory utilization
- Instance count (current, min, max)
- Billable container time
- Request/response sizes

**Custom Metrics**:
The application uses structured logging which can be converted to metrics using log-based metrics in Cloud Monitoring.

**Alerting**:
Create alerts for:
- High error rates (5xx responses)
- Increased latency (p95, p99)
- Resource exhaustion (CPU/memory)
- Instance scaling events

### Cloud Trace

**Distributed Tracing**:
Enable Cloud Trace to track requests across services. Correlation IDs in logs help trace requests through the Master → Pub/Sub → Worker agent flow.

**Performance Analysis**:
Identify bottlenecks in the request pipeline:
- LLM API call latency
- Neo4j query performance
- Vector search duration
- Inter-service communication

### Health Checks

**Endpoint Monitoring**:
Each service exposes a `/health` endpoint. The Master Agent endpoint is publicly accessible for external monitoring.

**Liveness Probes**:
Cloud Run performs automatic health checks. Configure custom health check paths if needed.

**Readiness**:
Services report database connectivity status in health responses. Use this to detect Neo4j connection issues.

## Cost Analysis

### Cloud Run Pricing

**Compute Costs**:
- Billed per 100ms of CPU time and GB-second of memory
- Minimum charge per request
- Free tier: 2 million requests, 360,000 GB-seconds, 180,000 vCPU-seconds per month

**Unified Container vs Separate Services**:
- Single service reduces networking overhead
- Shared resource pool more efficient for low traffic
- Lower minimum instance costs (1 vs 4-5 services)
- Estimated savings: 30-40% for small-to-medium workloads

**Cost Factors**:
- Number of requests per month
- Average request duration
- CPU and memory allocation
- Minimum instances (always-on costs)
- Egress traffic (minimal for API responses)

### Additional Costs

**Secret Manager**:
- $0.06 per 10,000 secret access operations
- Minimal cost (secrets accessed at startup)

**Artifact Registry**:
- $0.10 per GB per month for storage
- Minimal cost (few GB for images)

**Cloud Logging**:
- First 50 GB per month free
- $0.50 per GB after free tier
- Typical usage: 1-5 GB per month

**External Services**:
- Neo4j Aura: $65-200+ per month (depends on size)
- Google Gemini API: Pay per token (varies by usage)

## Security Considerations

### Secret Management

**Best Practices**:
- Rotate secrets regularly (Neo4j password, API keys)
- Use Secret Manager versioning for rollback capability
- Never commit secrets to version control
- Audit secret access logs

**IAM Permissions**:
- Follow principle of least privilege
- Create dedicated service accounts per environment
- Regularly review and audit IAM bindings
- Use workload identity for GKE if migrating

### Network Security

**Public Access**:
The default configuration allows public access to the API. For production:
- Implement authentication (API keys, OAuth, JWT)
- Use Cloud Armor for DDoS protection
- Configure VPC Service Controls for data exfiltration prevention
- Add rate limiting to prevent abuse

**Private Connectivity**:
- Use VPC connector for private Neo4j access
- Configure Private Service Connect for Gemini API
- Implement Cloud NAT for controlled egress

### Data Protection

**PII Handling**:
- The system includes PII redaction for conversations
- Verify redaction patterns match your compliance requirements
- Consider additional encryption for sensitive data
- Implement data retention policies

**Compliance**:
- Review data residency requirements (choose appropriate region)
- Implement audit logging for compliance tracking
- Configure data loss prevention (DLP) if needed
- Document data flows for GDPR/CCPA compliance

## Related Documentation

For detailed information about the system architecture and components, see the `services/` directory README.
