#!/bin/bash

# Setup GCP Secrets for Cloud Run deployment
# Usage: ./setup-secrets.sh

set -e

echo "🔐 Setting up GCP Secrets"
echo "========================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Enable Secret Manager API
echo "Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com
echo ""

# Prompt for secrets
echo "Please provide the following credentials:"
echo ""

read -p "Neo4j URI (e.g., neo4j+s://xxx.databases.neo4j.io): " NEO4J_URI
read -p "Neo4j User (default: neo4j): " NEO4J_USER
NEO4J_USER=${NEO4J_USER:-neo4j}
read -sp "Neo4j Password: " NEO4J_PASSWORD
echo ""
read -sp "Gemini API Key: " GEMINI_API_KEY
echo ""
read -sp "App Secret Key (for encryption): " SECRET_KEY
echo ""
echo ""

# Create secrets
echo "Creating secrets in Secret Manager..."

echo -n "$NEO4J_URI" | gcloud secrets create neo4j-uri --data-file=- 2>/dev/null || \
  echo -n "$NEO4J_URI" | gcloud secrets versions add neo4j-uri --data-file=-
echo "✅ neo4j-uri"

echo -n "$NEO4J_USER" | gcloud secrets create neo4j-user --data-file=- 2>/dev/null || \
  echo -n "$NEO4J_USER" | gcloud secrets versions add neo4j-user --data-file=-
echo "✅ neo4j-user"

echo -n "$NEO4J_PASSWORD" | gcloud secrets create neo4j-password --data-file=- 2>/dev/null || \
  echo -n "$NEO4J_PASSWORD" | gcloud secrets versions add neo4j-password --data-file=-
echo "✅ neo4j-password"

echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=- 2>/dev/null || \
  echo -n "$GEMINI_API_KEY" | gcloud secrets versions add gemini-api-key --data-file=-
echo "✅ gemini-api-key"

echo -n "$SECRET_KEY" | gcloud secrets create app-secret-key --data-file=- 2>/dev/null || \
  echo -n "$SECRET_KEY" | gcloud secrets versions add app-secret-key --data-file=-
echo "✅ app-secret-key"

echo ""
echo "🎉 Secrets created successfully!"
echo ""
echo "Next steps:"
echo "1. Run ./deploy.sh to deploy all agents"
echo "2. Or follow DEPLOY_TO_CLOUD_RUN.md for manual deployment"
echo ""
