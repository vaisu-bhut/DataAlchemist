# Agentic Workflow - Terraform Deployment

Deploy the unified agentic system to Google Cloud Run as a **single container**.

## 📁 File Structure

```
terraform/
├── provider.tf             # GCP provider configuration
├── variables.tf            # Input variables
├── outputs.tf              # Output values
├── versions.tf             # Terraform version constraints
├── apis.tf                 # Enable GCP APIs
├── artifact_registry.tf    # Container registry
├── secrets.tf              # Secret Manager secrets
├── agentic_system.tf       # Unified Cloud Run service (all 4 agents)
└── terraform.tfvars        # Your configuration (create from example)
```

## 🏗️ Architecture

This Terraform configuration deploys a **single Cloud Run service** containing all 4 agents:

```
┌─────────────────────────────────────────┐
│   Cloud Run: agentic-system             │
│                                         │
│   ┌─────────────────────────────────┐   │
│   │ Supervisord Process Manager     │   │
│   └─────────────────────────────────┘   │
│                                         │
│   ┌──────────┐  ┌──────────┐          │
│   │ Pub/Sub  │  │  Master  │          │
│   │  :8001   │◄─┤  :8000   │ ← Exposed│
│   └──────────┘  └──────────┘          │
│                                         │
│   ┌──────────┐  ┌──────────┐          │
│   │  Ingest  │  │   Chat   │          │
│   │  :8002   │  │  :8003   │          │
│   └──────────┘  └──────────┘          │
│                                         │
│   All communicate via localhost        │
└─────────────────────────────────────────┘
```

**Benefits:**
- ✅ Single deployment unit
- ✅ Faster inter-service communication (localhost)
- ✅ Simpler management
- ✅ Lower cost (one service vs four)

## 🚀 Quick Start

### 1. Prerequisites & Setup
```bash
# Set your project ID
export PROJECT_ID=your-project-id

# Run setup script (enables APIs, creates service accounts)
chmod +x setup.sh
./setup.sh

# Or on Windows:
# set PROJECT_ID=your-project-id
# setup.bat

# Authenticate
gcloud auth login
gcloud auth application-default login
```

**What the setup script does:**
- Enables Cloud Run, Secret Manager, Artifact Registry, Compute APIs
- Creates default compute service account
- Verifies setup

**Manual setup:** See `SETUP.md` for detailed instructions

### 2. Configure
```bash
cd terraform

# Copy example
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

**Required values in terraform.tfvars:**
- `project_id` - Your GCP project ID
- `region` - GCP region (default: us-central1)
- `cloud_run_service_account` - Service account email
- `neo4j_uri` - Neo4j connection string
- `neo4j_password` - Neo4j password
- `gemini_api_key` - Gemini API key
- `secret_key` - Random secret (generate: `openssl rand -hex 32`)

**How it works:**
1. You provide values in `terraform.tfvars`
2. Terraform creates secrets in Secret Manager with these values
3. Cloud Run fetches secrets at runtime (not from Terraform)

### 3. Deploy Everything
```bash
# Initialize
terraform init

# Preview
terraform plan

# Deploy (creates everything)
terraform apply
```

Type `yes` when prompted.

**This creates:**
1. Artifact Registry repository
2. Secret Manager secrets **with values from terraform.tfvars**
3. IAM permissions
4. Cloud Run service (fetches secrets at runtime)

**How secrets work:**
- Terraform stores your values in Secret Manager
- Cloud Run fetches secrets when container starts
- No secrets in Docker images or Git

### 4. Get URL and Test
```bash
SERVICE_URL=$(terraform output -raw service_url)

# Health check
curl $SERVICE_URL/health

# Test ingest
curl -X POST $SERVICE_URL/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{"conversations": [...]}'

# Test chat
curl -X POST $SERVICE_URL/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I reset my password?"}'
```

## 🔄 CI/CD Workflow

### GitHub Actions automatically:
1. **Builds** unified container image (all 4 services)
2. **Pushes** to Artifact Registry
3. Cloud Run **pulls latest image** on next deployment

### Setup:
1. Add GitHub secrets (see `.github/workflows/deploy-agents.yml`)
2. Push to main branch
3. Automatic build and push!
4. Run `terraform apply` to deploy latest image

**Note:** Terraform manages the Cloud Run service. GitHub Actions only builds and pushes the Docker image.

## 📦 What Gets Deployed

### Single Cloud Run Service
- **Service name**: `agentic-system`
- **Exposed port**: 8000 (Master Agent)
- **Internal services**:
  - Pub/Sub (port 8001) - Message routing
  - Master Agent (port 8000) - API gateway
  - Ingest Agent (port 8002) - Data processing
  - Chat Agent (port 8003) - Conversational
- **Resources**: 4Gi memory, 2 CPUs (shared)
- **Scaling**: Min 1, Max 10 instances

### Infrastructure
- Artifact Registry repository
- Secret Manager secrets (2):
  - `database-credentials` (Neo4j)
  - `api-keys` (Gemini, app secret)
- IAM permissions
- Auto-scaling configuration

## 🔧 Customization

### Scale the service
Edit `agentic_system.tf`:
```hcl
metadata {
  annotations = {
    "autoscaling.knative.dev/maxScale" = "20"  # Increase max instances
    "autoscaling.knative.dev/minScale" = "2"   # Keep 2 instances warm
  }
}
```

Then apply:
```bash
terraform apply
```

### Adjust resources
Edit `agentic_system.tf`:
```hcl
resources {
  limits = {
    cpu    = "4000m"  # 4 CPUs (shared by all services)
    memory = "8Gi"    # 8GB RAM (shared by all services)
  }
}
```

**Note:** All 4 services share the allocated resources within the container.

## 🗑️ Destroy

```bash
terraform destroy
```

This removes all Cloud Run services and secrets.

## 📊 Monitoring

### View logs
```bash
# All services (unified container)
gcloud run services logs read agentic-system --region=us-central1

# Follow logs in real-time
gcloud run services logs tail agentic-system --region=us-central1

# Filter by service
gcloud run services logs read agentic-system --region=us-central1 | grep "master-agent"
gcloud run services logs read agentic-system --region=us-central1 | grep "ingest-agent"
gcloud run services logs read agentic-system --region=us-central1 | grep "chat-agent"
gcloud run services logs read agentic-system --region=us-central1 | grep "pubsub"
```

### Cloud Console
```
https://console.cloud.google.com/run?project=YOUR_PROJECT_ID
```

### Check service status
```bash
gcloud run services describe agentic-system --region=us-central1
```

## 🔍 Troubleshooting

### Service not starting
```bash
# Check logs
gcloud run services logs read agentic-system --region=us-central1

# Check supervisord logs
gcloud run services logs read agentic-system --region=us-central1 | grep "supervisord"

# Common issues:
# - Wrong Neo4j URI
# - Invalid API keys
# - Image not found (check GitHub Actions)
# - One service failing prevents others from starting
```

### One service not responding
```bash
# Check which services are running
gcloud run services logs read agentic-system --region=us-central1 | grep "program:"

# Check for errors in specific service
gcloud run services logs read agentic-system --region=us-central1 | grep "ERROR"
```

### Terraform errors
```bash
# Refresh state
terraform refresh

# View state
terraform state list

# Force unlock if stuck
terraform force-unlock LOCK_ID
```

### Images not found
Check GitHub Actions workflow completed successfully:
```
https://github.com/YOUR_USERNAME/YOUR_REPO/actions
```

## 💰 Cost Estimates

**Unified Container (vs 4 separate services):**
- **Development**: ~$5-10/month (1 service vs 4)
- **Production**: ~$100-200/month (lower networking costs)
- Plus Neo4j Aura and Gemini API usage

**Savings:** ~30-40% compared to separate services

## 📚 Documentation

- **Architecture**: `../services/ARCHITECTURE.md`
- **Agent Details**: `../services/AGENTS_README.md`
- **Quick Reference**: `../services/QUICK_REFERENCE.md`

## ✅ Deployment Checklist

- [ ] GCP project created
- [ ] Billing enabled
- [ ] `terraform.tfvars` configured
- [ ] GitHub secrets added (for CI/CD)
- [ ] `terraform init` completed
- [ ] `terraform apply` successful
- [ ] Health checks passing
- [ ] API tested

---

**Deploy with:** `terraform apply` 🚀
