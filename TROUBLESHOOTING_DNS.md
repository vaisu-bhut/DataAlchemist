# DNS Resolution Error - Troubleshooting Guide

## Error Message
```json
{"detail": "[Errno -3] Temporary failure in name resolution"}
```

## What This Means
The agent cannot resolve the hostname (likely trying to connect to Neo4j or Pub/Sub service).

## Common Causes

### 1. Neo4j Connection Issue
**Most Likely Cause:** Neo4j URI is incorrect or Neo4j is not accessible from Cloud Run.

**Check:**
```bash
# View your Neo4j URI
cd terraform
terraform output -raw neo4j_uri  # This won't work as it's a secret

# Check secrets
gcloud secrets versions access latest --secret=database-credentials
```

**Fix:**
Ensure your Neo4j URI is correct in `terraform.tfvars`:
```hcl
neo4j_uri = "neo4j+s://xxxxx.databases.neo4j.io"  # Must use neo4j+s:// for Aura
```

### 2. PUBSUB_URL Not Set
**Cause:** Environment variable not being passed correctly.

**Check Logs:**
```bash
gcloud run services logs read ingest-agent --region=us-east1 --limit=50
gcloud run services logs read chat-agent --region=us-east1 --limit=50
```

Look for: `"pubsub_url": "http://..."`

**Fix:**
Already handled in Terraform - PUBSUB_URL is set from `google_cloud_run_service.pubsub.status[0].url`

### 3. Network Connectivity
**Cause:** Cloud Run cannot reach external services.

**Check:**
- Neo4j Aura should be publicly accessible
- No VPC restrictions
- Firewall allows Cloud Run IPs

## Quick Diagnosis

### Step 1: Check Logs
```bash
# Check which service is failing
gcloud run services logs read master-agent --region=us-east1 --limit=20
gcloud run services logs read ingest-agent --region=us-east1 --limit=20
gcloud run services logs read chat-agent --region=us-east1 --limit=20
```

### Step 2: Check Secrets
```bash
# View database credentials
gcloud secrets versions access latest --secret=database-credentials | jq .

# Should show:
# {
#   "neo4j_uri": "neo4j+s://xxxxx.databases.neo4j.io",
#   "neo4j_user": "neo4j",
#   "neo4j_password": "..."
# }
```

### Step 3: Test Neo4j Connection
From your local machine:
```bash
# Install neo4j driver
pip install neo4j

# Test connection
python3 << EOF
from neo4j import GraphDatabase
import os

uri = "neo4j+s://xxxxx.databases.neo4j.io"  # Your URI
user = "neo4j"
password = "your-password"

driver = GraphDatabase.driver(uri, auth=(user, password))
try:
    driver.verify_connectivity()
    print("✅ Neo4j connection successful")
except Exception as e:
    print(f"❌ Neo4j connection failed: {e}")
finally:
    driver.close()
EOF
```

## Solutions

### Solution 1: Fix Neo4j URI
If using Neo4j Aura, ensure URI format is correct:

```hcl
# In terraform.tfvars
neo4j_uri = "neo4j+s://xxxxx.databases.neo4j.io"  # ✅ Correct
# NOT:
# neo4j_uri = "bolt://xxxxx.databases.neo4j.io"   # ❌ Wrong for Aura
# neo4j_uri = "neo4j://xxxxx.databases.neo4j.io"  # ❌ Wrong for Aura
```

Then redeploy:
```bash
cd terraform
terraform apply
```

### Solution 2: Update Secrets
If Neo4j credentials changed:

```bash
# Update database credentials secret
echo '{
  "neo4j_uri": "neo4j+s://xxxxx.databases.neo4j.io",
  "neo4j_user": "neo4j",
  "neo4j_password": "new-password"
}' | gcloud secrets versions add database-credentials --data-file=-

# Redeploy services to pick up new secret
cd terraform
terraform apply -replace=google_cloud_run_service.ingest
terraform apply -replace=google_cloud_run_service.chat
```

### Solution 3: Check Neo4j Firewall
In Neo4j Aura console:
1. Go to your database
2. Check "Connection" tab
3. Ensure "Allow from anywhere" is enabled
4. Or add Cloud Run IP ranges

### Solution 4: Increase Timeout
If connection is slow:

Edit `terraform/ingest_agent.tf` and `terraform/chat_agent.tf`:
```hcl
timeout_seconds = 600  # Increase from 300/60
```

Then apply:
```bash
cd terraform
terraform apply
```

## Verify Fix

### 1. Check Logs Again
```bash
gcloud run services logs read ingest-agent --region=us-east1 --limit=20
```

Look for:
- ✅ "Connected to Neo4j"
- ✅ "Ingest agent ready"
- ❌ "Temporary failure in name resolution"

### 2. Test Health Endpoint
```bash
MASTER_URL=$(cd terraform && terraform output -raw master_url)
curl $MASTER_URL/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "master-agent-langgraph",
  "version": "2.0.0"
}
```

### 3. Test Ingest
```bash
curl -X POST $MASTER_URL/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{"conversations": [...]}'
```

Should NOT return DNS error.

## Still Having Issues?

### Get Detailed Logs
```bash
# Stream logs in real-time
gcloud run services logs tail ingest-agent --region=us-east1

# Get full error trace
gcloud run services logs read ingest-agent \
  --region=us-east1 \
  --limit=100 \
  --format=json | jq '.textPayload'
```

### Check Service Configuration
```bash
# View environment variables
gcloud run services describe ingest-agent \
  --region=us-east1 \
  --format=yaml | grep -A 20 "env:"
```

### Test Locally
Build and run container locally to test:
```bash
cd services

# Build
docker build -t ingest-test -f agents/ingest/Dockerfile .

# Run with your credentials
docker run -p 8002:8002 \
  -e DATABASE_CREDENTIALS='{"neo4j_uri":"...","neo4j_user":"neo4j","neo4j_password":"..."}' \
  -e API_KEYS='{"gemini_api_key":"..."}' \
  -e PUBSUB_URL="http://host.docker.internal:8001" \
  ingest-test
```

## Prevention

### Use Correct Neo4j URI Format
- ✅ `neo4j+s://` for Neo4j Aura (encrypted)
- ✅ `bolt://` for local Neo4j
- ✅ `neo4j://` for unencrypted (not recommended)

### Test Before Deploying
```bash
# Test Neo4j connection locally first
python3 -c "from neo4j import GraphDatabase; GraphDatabase.driver('neo4j+s://...', auth=('neo4j', 'password')).verify_connectivity(); print('OK')"
```

### Monitor Logs
Set up log-based alerts in Cloud Console for DNS errors.

---

**Most Common Fix:** Update Neo4j URI to use `neo4j+s://` format in `terraform.tfvars` and run `terraform apply`.
