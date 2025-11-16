# Agentic Workflow - Terraform Deployment

Deploy the complete multi-agent system to Google Cloud Run.

## 📁 File Structure

```
terraform/
├── main.tf                 # Main entry point & Terraform config
├── provider.tf             # GCP provider configuration
├── variables.tf            # Input variables
├── outputs.tf              # Output values
├── apis.tf                 # Enable GCP APIs
├── artifact_registry.tf    # Container registry
├── secrets.tf              # Secret Manager secrets
├── pubsub_service.tf       # Pub/Sub message routing
├── master_agent.tf         # Master orchestrator
├── ingest_agent.tf         # Data processing worker
├── chat_agent.tf           # Conversational worker
└── terraform.tfvars        # Your configuration (create from example)
```

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

**Required values:**
- `project_id` - Your GCP project ID
- `neo4j_uri` - Neo4j connection string
- `neo4j_password` - Neo4j password
- `gemini_api_key` - Gemini API key
- `secret_key` - Application secret (random string)

### 3. Deploy
```bash
# Initialize
terraform init

# Preview
terraform plan

# Deploy
terraform apply
```

Type `yes` when prompted.

### 4. Get URLs
```bash
terraform output
```

### 5. Test
```bash
MASTER_URL=$(terraform output -raw master_url)
curl $MASTER_URL/health
```

## 🔄 CI/CD Workflow

### GitHub Actions automatically:
1. **Builds** all 4 container images
2. **Pushes** to Artifact Registry
3. **Deploys** with Terraform

### Setup:
1. Add GitHub secrets (see `.github/workflows/deploy-agents.yml`)
2. Push to main branch
3. Automatic deployment!

## 📦 What Gets Deployed

### Services (4)
- **Pub/Sub** (Port 8001) - Message routing
- **Master Agent** (Port 8000) - API gateway
- **Ingest Agent** (Port 8002) - Data processing
- **Chat Agent** (Port 8003) - Conversational

### Infrastructure
- Artifact Registry repository
- Secret Manager secrets (5)
- IAM permissions
- Auto-scaling configuration

## 🔧 Customization

### Scale a service
Edit the service file (e.g., `chat_agent.tf`):
```hcl
metadata {
  annotations = {
    "autoscaling.knative.dev/maxScale" = "50"  # Increase
    "autoscaling.knative.dev/minScale" = "2"   # Keep warm
  }
}
```

Then apply:
```bash
terraform apply
```

### Adjust resources
```hcl
resources {
  limits = {
    cpu    = "2000m"  # 2 CPUs
    memory = "4Gi"    # 4GB RAM
  }
}
```

## 🗑️ Destroy

```bash
terraform destroy
```

This removes all Cloud Run services and secrets.

## 📊 Monitoring

### View logs
```bash
gcloud run services logs read master-agent --region=us-central1
gcloud run services logs read ingest-agent --region=us-central1
gcloud run services logs read chat-agent --region=us-central1
gcloud run services logs read pubsub --region=us-central1
```

### Cloud Console
```
https://console.cloud.google.com/run?project=YOUR_PROJECT_ID
```

## 🔍 Troubleshooting

### Service not starting
```bash
# Check logs
gcloud run services logs read SERVICE_NAME --region=us-central1

# Common issues:
# - Wrong Neo4j URI
# - Invalid API keys
# - Image not found (check GitHub Actions)
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

- **Development**: ~$10-20/month
- **Production**: ~$150-300/month
- Plus Neo4j Aura and Gemini API usage

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
