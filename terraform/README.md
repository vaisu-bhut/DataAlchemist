# Terraform Deployment Guide

This directory contains Terraform configuration to deploy the Knowledge Engine API to Google Cloud Run.

## What Gets Deployed

- **Artifact Registry**: Docker repository for container images
- **Cloud Run**: Serverless container deployment with auto-scaling
- **IAM**: Service accounts and permissions for GitHub Actions CI/CD

Environment variables (including secrets) are passed directly from your `terraform.tfvars` file to Cloud Run.

## Prerequisites

1. **GCP Account**: Active project with billing enabled
2. **Neo4j Database**: Neo4j Aura instance or hosted Neo4j
   - Get free tier at [neo4j.com/cloud/aura](https://neo4j.com/cloud/aura)
   - Note your connection URI (e.g., `bolt://xxxxx.databases.neo4j.io:7687`)
3. **Gemini API Key**: From [Google AI Studio](https://aistudio.google.com/app/apikey)
4. **Tools Installed**:
   - Terraform >= 1.0
   - gcloud CLI
   - Docker

## Quick Start

### 1. Enable GCP APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### 2. Build and Push Docker Image

```bash
# From project root
cd services

# Build
docker build -t knowledge-engine:latest .

# Tag for your project (replace YOUR_PROJECT_ID)
docker tag knowledge-engine:latest \
  us-central1-docker.pkg.dev/YOUR_PROJECT_ID/dataalchemist/knowledge-engine:latest

# Configure Docker auth
gcloud auth configure-docker us-central1-docker.pkg.dev

# Push
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/dataalchemist/knowledge-engine:latest
```

### 3. Configure Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your values:

```hcl
project_id = "your-gcp-project-id"
region     = "us-central1"

github_owner = "your-github-username"
github_repo  = "your-repo-name"

neo4j_uri      = "bolt://xxxxx.databases.neo4j.io:7687"
neo4j_user     = "neo4j"
neo4j_password = "your-neo4j-password"

gemini_api_key = "your-gemini-api-key"
app_secret_key = "generate-a-random-secret-key"
```

### 4. Deploy

```bash
terraform init
terraform plan
terraform apply
```

Type `yes` when prompted.

### 5. Get Your API URL

```bash
terraform output cloud_run_url
```

This outputs your public Cloud Run URL, e.g.:
```
https://knowledge-engine-api-xxxxx-uc.a.run.app
```

## Testing the Deployment

```bash
# Store the URL
export API_URL=$(terraform output -raw cloud_run_url)

# Health check
curl $API_URL/health

# API docs
echo "Swagger UI: $API_URL/docs"
```

## Configuration

### Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `project_id` | GCP project ID | Yes | - |
| `region` | GCP region | No | `us-central1` |
| `neo4j_uri` | Neo4j connection URI | Yes | - |
| `neo4j_user` | Neo4j username | No | `neo4j` |
| `neo4j_password` | Neo4j password | Yes | - |
| `gemini_api_key` | Gemini API key | Yes | - |
| `app_secret_key` | App encryption key | Yes | - |
| `similarity_threshold` | Similarity matching threshold | No | `0.85` |
| `confidence_threshold` | Response confidence threshold | No | `0.7` |
| `max_retrieval_results` | Max search results | No | `10` |

### Outputs

| Output | Description |
|--------|-------------|
| `cloud_run_url` | Public URL endpoint for the API |
| `service_name` | Cloud Run service name |
| `artifact_registry_repository` | Docker repository URL |

## Cloud Run Configuration

The service is configured with:
- **CPU**: 2 vCPU
- **Memory**: 2 GiB
- **Scaling**: 0 to 10 instances (scales to zero when idle)
- **Ingress**: All traffic allowed
- **Authentication**: Public (unauthenticated)

To modify these settings, edit the `google_cloud_run_v2_service` resource in `main.tf`.

## Security

Sensitive values (Neo4j password, Gemini API key, app secret key) are:
- Stored in your local `terraform.tfvars` file (gitignored)
- Stored in GitHub Secrets for CI/CD
- Passed as environment variables to Cloud Run at deployment time

**Important**: Never commit `terraform.tfvars` to version control. It's already in `.gitignore`.

## Cost Optimization

Cloud Run pricing is based on:
- Request count
- CPU/memory usage during request processing
- Idle time (minimal cost)

With `min_instance_count = 0`, the service scales to zero when not in use, minimizing costs.

## Updating the Deployment

After making changes to your application:

1. **Rebuild and push the Docker image**:
   ```bash
   cd services
   docker build -t knowledge-engine:latest .
   docker tag knowledge-engine:latest \
     us-central1-docker.pkg.dev/YOUR_PROJECT_ID/dataalchemist/knowledge-engine:latest
   docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/dataalchemist/knowledge-engine:latest
   ```

2. **Redeploy** (if Terraform config changed):
   ```bash
   cd terraform
   terraform apply
   ```

3. **Or force new revision** (if only code changed):
   ```bash
   gcloud run services update knowledge-engine-api \
     --region us-central1 \
     --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/dataalchemist/knowledge-engine:latest
   ```

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

Type `yes` when prompted. This will delete:
- Cloud Run service
- Secrets in Secret Manager
- Artifact Registry repository
- Service accounts

**Note**: This does NOT delete your Neo4j database.

## Troubleshooting

**Cloud Run service fails to start**:
- Check logs: `gcloud run services logs read knowledge-engine-api --region us-central1`
- Verify Neo4j connection URI is correct
- Ensure all required variables are set in `terraform.tfvars`

**Cannot push Docker image**:
- Authenticate: `gcloud auth configure-docker us-central1-docker.pkg.dev`
- Verify Artifact Registry exists: `gcloud artifacts repositories list`

**Terraform apply fails**:
- Ensure all required APIs are enabled
- Check IAM permissions for your user account
- Verify `terraform.tfvars` has all required values

## Next Steps

- Set up CI/CD with GitHub Actions (service account already created)
- Add authentication to the API
- Configure custom domain (requires Cloud Load Balancer)
- Set up monitoring and alerting
- Implement rate limiting
