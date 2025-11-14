#!/bin/bash

# Deploy all agents to GCP Cloud Run
# Usage: ./deploy.sh

set -e

echo "🚀 Deploying Agentic System to Cloud Run"
echo "=========================================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

REGION=$(gcloud config get-value run/region)
if [ -z "$REGION" ]; then
    REGION="us-central1"
    echo "⚠️  No region set, using default: $REGION"
fi

echo "📋 Configuration:"
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo ""

# Deploy Pub/Sub
echo "1️⃣  Deploying Pub/Sub Service..."
cd pubsub
gcloud builds submit --tag gcr.io/$PROJECT_ID/pubsub --quiet
gcloud run deploy pubsub \
  --image gcr.io/$PROJECT_ID/pubsub \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8001 \
  --memory 256Mi \
  --min-instances 1 \
  --max-instances 3 \
  --quiet

PUBSUB_URL=$(gcloud run services describe pubsub --region $REGION --format 'value(status.url)')
echo "✅ Pub/Sub deployed: $PUBSUB_URL"
echo ""

# Deploy Master Agent
echo "2️⃣  Deploying Master Agent..."
cd ../agents/master
gcloud builds submit --tag gcr.io/$PROJECT_ID/master-agent --quiet
gcloud run deploy master-agent \
  --image gcr.io/$PROJECT_ID/master-agent \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8000 \
  --memory 512Mi \
  --min-instances 1 \
  --max-instances 5 \
  --set-env-vars PUBSUB_URL=$PUBSUB_URL \
  --quiet

MASTER_URL=$(gcloud run services describe master-agent --region $REGION --format 'value(status.url)')
echo "✅ Master Agent deployed: $MASTER_URL"
echo ""

# Deploy Ingest Agent
echo "3️⃣  Deploying Ingest Agent..."
cd ../ingest
gcloud builds submit --tag gcr.io/$PROJECT_ID/ingest-agent --quiet
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
  --set-secrets NEO4J_URI=neo4j-uri:latest \
  --set-secrets NEO4J_USER=neo4j-user:latest \
  --set-secrets NEO4J_PASSWORD=neo4j-password:latest \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest \
  --set-secrets SECRET_KEY=app-secret-key:latest \
  --quiet

echo "✅ Ingest Agent deployed"
echo ""

# Deploy Chat Agent
echo "4️⃣  Deploying Chat Agent..."
cd ../chat
gcloud builds submit --tag gcr.io/$PROJECT_ID/chat-agent --quiet
gcloud run deploy chat-agent \
  --image gcr.io/$PROJECT_ID/chat-agent \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8003 \
  --memory 1Gi \
  --min-instances 1 \
  --max-instances 20 \
  --timeout 60 \
  --set-env-vars PUBSUB_URL=$PUBSUB_URL \
  --set-env-vars GEMINI_MODEL_NAME=gemini-2.5-pro \
  --set-env-vars GEMINI_EMBEDDING_MODEL=models/text-embedding-004 \
  --set-secrets NEO4J_URI=neo4j-uri:latest \
  --set-secrets NEO4J_USER=neo4j-user:latest \
  --set-secrets NEO4J_PASSWORD=neo4j-password:latest \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest \
  --set-secrets SECRET_KEY=app-secret-key:latest \
  --quiet

echo "✅ Chat Agent deployed"
echo ""

# Summary
echo "=========================================="
echo "🎉 Deployment Complete!"
echo "=========================================="
echo ""
echo "📍 Service URLs:"
echo "   Master Agent: $MASTER_URL"
echo "   Pub/Sub:      $PUBSUB_URL"
echo ""
echo "🧪 Test your deployment:"
echo "   curl $MASTER_URL/health"
echo ""
echo "📊 View logs:"
echo "   gcloud run services logs read master-agent --region $REGION"
echo ""
echo "💰 Monitor costs:"
echo "   https://console.cloud.google.com/billing"
echo ""
