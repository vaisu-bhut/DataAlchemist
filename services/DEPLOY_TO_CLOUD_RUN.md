# Deploy to GCP Cloud Run - Step by Step

## Prerequisites

1. **GCP Account** with billing enabled
2. **gcloud CLI** installed: https://cloud.google.com/sdk/docs/install
3. **Docker** installed locally
4. **Neo4j Aura** database (or Neo4j instance accessible from internet)

## Step 1: Setup GCP Project

```bash
# Login to GCP
gcloud auth login

# Create new project (or use existing)
export PROJECT_ID="your-project-name"
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Set region
export REGION="us-central1"
gcloud config set run/region $REGION
```

## Step 2: Create Secrets

Store sensitive data in Secret Manager:

```bash
# Neo4j credentials
echo -n "neo4j+s://your-instance.databases.neo4j.io" | \
  gcloud secrets create neo4j-uri --data-file=-

echo -n "neo4j" | \
  gcloud secrets create neo4j-user --data-file=-

echo -n "your-neo4j-password" | \
  gcloud secrets create neo4j-password --data-file=-

# Gemini API key
echo -n "your-gemini-api-key" | \
  gcloud secrets create gemini-api-key --data-file=-

# Other secrets
echo -n "your-secret-key-for-app" | \
  gcloud secrets create app-secret-key --data-file=-
```

## Step 3: Deploy Pub/Sub Service

```bash
cd services/pubsub

# Build and push to Container Registry
gcloud builds submit --tag gcr.io/$PROJECT_ID/pubsub

# Deploy to Cloud Run
gcloud run deploy pubsub \
  --image gcr.io/$PROJECT_ID/pubsub \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8001 \
  --memory 256Mi \
  --cpu 1 \
  --min-instances 1 \
  --max-instances 3

# Get the URL
export PUBSUB_URL=$(gcloud run services describe pubsub \
  --region $REGION \
  --format 'value(status.url)')

echo "Pub/Sub URL: $PUBSUB_URL"
```

## Step 4: Deploy Master Agent

```bash
cd ../agents/master

# Build and push
gcloud builds submit --tag gcr.io/$PROJECT_ID/master-agent

# Deploy to Cloud Run
gcloud run deploy master-agent \
  --image gcr.io/$PROJECT_ID/master-agent \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8000 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 1 \
  --max-instances 5 \
  --set-env-vars PUBSUB_URL=$PUBSUB_URL

# Get the URL
export MASTER_URL=$(gcloud run services describe master-agent \
  --region $REGION \
  --format 'value(status.url)')

echo "Master Agent URL: $MASTER_URL"
```

## Step 5: Deploy Ingest Agent

```bash
cd ../ingest

# Build and push
gcloud builds submit --tag gcr.io/$PROJECT_ID/ingest-agent

# Deploy to Cloud Run with secrets
gcloud run deploy ingest-agent \
  --image gcr.io/$PROJECT_ID/ingest-agent \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8002 \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --set-env-vars PUBSUB_URL=$PUBSUB_URL \
  --set-env-vars GEMINI_MODEL_NAME=gemini-2.5-pro \
  --set-env-vars GEMINI_EMBEDDING_MODEL=models/text-embedding-004 \
  --set-env-vars CHUNK_SIZE=2000 \
  --set-env-vars SIMILARITY_THRESHOLD=0.85 \
  --set-env-vars CONFIDENCE_THRESHOLD=0.7 \
  --set-env-vars MAX_RETRIEVAL_RESULTS=10 \
  --set-secrets NEO4J_URI=neo4j-uri:latest \
  --set-secrets NEO4J_USER=neo4j-user:latest \
  --set-secrets NEO4J_PASSWORD=neo4j-password:latest \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest \
  --set-secrets SECRET_KEY=app-secret-key:latest

echo "Ingest Agent deployed"
```

## Step 6: Deploy Chat Agent

```bash
cd ../chat

# Build and push
gcloud builds submit --tag gcr.io/$PROJECT_ID/chat-agent

# Deploy to Cloud Run with secrets
gcloud run deploy chat-agent \
  --image gcr.io/$PROJECT_ID/chat-agent \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8003 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 1 \
  --max-instances 20 \
  --timeout 60 \
  --set-env-vars PUBSUB_URL=$PUBSUB_URL \
  --set-env-vars GEMINI_MODEL_NAME=gemini-2.5-pro \
  --set-env-vars GEMINI_EMBEDDING_MODEL=models/text-embedding-004 \
  --set-env-vars CHUNK_SIZE=2000 \
  --set-env-vars SIMILARITY_THRESHOLD=0.85 \
  --set-env-vars CONFIDENCE_THRESHOLD=0.7 \
  --set-env-vars MAX_RETRIEVAL_RESULTS=10 \
  --set-secrets NEO4J_URI=neo4j-uri:latest \
  --set-secrets NEO4J_USER=neo4j-user:latest \
  --set-secrets NEO4J_PASSWORD=neo4j-password:latest \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest \
  --set-secrets SECRET_KEY=app-secret-key:latest

echo "Chat Agent deployed"
```

## Step 7: Test Deployment

```bash
# Test Master Agent health
curl $MASTER_URL/health

# Test Ingest
curl -X POST $MASTER_URL/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "conversations": [{
      "conversation_id": "test_001",
      "customer_id": "customer_123",
      "agent_id": "agent_456",
      "messages": [
        {"role": "customer", "content": "I need help with my account"},
        {"role": "agent", "content": "I can help you with that"}
      ]
    }]
  }'

# Test Chat
curl -X POST $MASTER_URL/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I get help with my account?",
    "customer_id": "customer_123"
  }'
```

## Step 8: View Logs

```bash
# Master Agent logs
gcloud run services logs read master-agent --region $REGION --limit 50

# Ingest Agent logs
gcloud run services logs read ingest-agent --region $REGION --limit 50

# Chat Agent logs
gcloud run services logs read chat-agent --region $REGION --limit 50

# Pub/Sub logs
gcloud run services logs read pubsub --region $REGION --limit 50
```

## Step 9: Monitor Services

```bash
# List all services
gcloud run services list --region $REGION

# Get service details
gcloud run services describe master-agent --region $REGION
gcloud run services describe ingest-agent --region $REGION
gcloud run services describe chat-agent --region $REGION
gcloud run services describe pubsub --region $REGION
```

## Cost Optimization

### Set CPU Allocation
```bash
# Only allocate CPU during request processing
gcloud run services update ingest-agent --cpu-throttling --region $REGION
gcloud run services update chat-agent --cpu-throttling --region $REGION
```

### Adjust Scaling
```bash
# Scale to zero when idle (save costs)
gcloud run services update ingest-agent --min-instances 0 --region $REGION

# Keep chat agent warm for faster responses
gcloud run services update chat-agent --min-instances 2 --region $REGION
```

## Update an Agent

When you make changes to an agent:

```bash
# Example: Update Ingest Agent
cd services/agents/ingest

# Rebuild and push
gcloud builds submit --tag gcr.io/$PROJECT_ID/ingest-agent

# Deploy new version (Cloud Run will do rolling update)
gcloud run deploy ingest-agent \
  --image gcr.io/$PROJECT_ID/ingest-agent \
  --region $REGION
```

## Rollback

```bash
# List revisions
gcloud run revisions list --service ingest-agent --region $REGION

# Rollback to previous revision
gcloud run services update-traffic ingest-agent \
  --to-revisions REVISION_NAME=100 \
  --region $REGION
```

## Setup Custom Domain (Optional)

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service master-agent \
  --domain api.yourdomain.com \
  --region $REGION
```

## CI/CD with GitHub Actions

Create `.github/workflows/deploy-agents.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

env:
  PROJECT_ID: your-project-id
  REGION: us-central1

jobs:
  deploy-master:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - name: Deploy Master
        run: |
          cd services/agents/master
          gcloud builds submit --tag gcr.io/$PROJECT_ID/master-agent
          gcloud run deploy master-agent \
            --image gcr.io/$PROJECT_ID/master-agent \
            --region $REGION

  deploy-ingest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - name: Deploy Ingest
        run: |
          cd services/agents/ingest
          gcloud builds submit --tag gcr.io/$PROJECT_ID/ingest-agent
          gcloud run deploy ingest-agent \
            --image gcr.io/$PROJECT_ID/ingest-agent \
            --region $REGION

  # Similar for chat and pubsub...
```

## Troubleshooting

### Service won't start
```bash
# Check logs
gcloud run services logs read SERVICE_NAME --region $REGION --limit 100

# Check service status
gcloud run services describe SERVICE_NAME --region $REGION
```

### Secrets not accessible
```bash
# Grant Cloud Run service account access to secrets
gcloud secrets add-iam-policy-binding SECRET_NAME \
  --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

### Timeout issues
```bash
# Increase timeout
gcloud run services update SERVICE_NAME \
  --timeout 300 \
  --region $REGION
```

## Estimated Costs

**Development (low traffic)**:
- Master: ~$5/month
- Pub/Sub: ~$3/month
- Ingest: ~$10/month (scales to zero)
- Chat: ~$15/month
- **Total: ~$33/month**

**Production (moderate traffic)**:
- Master: ~$20/month
- Pub/Sub: ~$10/month
- Ingest: ~$50/month
- Chat: ~$100/month
- **Total: ~$180/month**

## Summary

✅ Each agent deployed independently
✅ Secrets managed securely
✅ Auto-scaling enabled
✅ Monitoring and logs available
✅ Cost-optimized configuration
✅ Ready for production traffic

---

**Your agents are now live on Cloud Run!** 🚀

Access your API at: `$MASTER_URL`
