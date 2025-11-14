# cURL Testing Guide - Quick Command Reference

## Get Your API URL

```bash
cd terraform
export MASTER_URL=$(terraform output -raw master_url)
echo $MASTER_URL
```

## Quick Tests

### 1. Health Check
```bash
curl $MASTER_URL/health
```

### 2. Ingest a Conversation
```bash
curl -X POST $MASTER_URL/api/v1/ingest \
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
            "content": "I cannot log into my account. My password is not working."
          },
          {
            "role": "agent",
            "content": "I can help you reset your password. Go to the login page and click Forgot Password. You will receive an email with a reset link within 5 minutes."
          },
          {
            "role": "customer",
            "content": "Got it! I received the email and reset my password. Thank you!"
          }
        ]
      }
    ]
  }'
```

### 3. Chat Query
```bash
curl -X POST $MASTER_URL/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I reset my password?",
    "customer_id": "customer_123"
  }'
```

## Pretty Print with jq

```bash
# Health check
curl -s $MASTER_URL/health | jq .

# Ingest
curl -s -X POST $MASTER_URL/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{"conversations": [...]}' | jq .

# Chat
curl -s -X POST $MASTER_URL/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}' | jq .
```

## Test All Services

```bash
# Get all URLs
cd terraform
export MASTER_URL=$(terraform output -raw master_url)
export PUBSUB_URL=$(terraform output -raw pubsub_url)
export INGEST_URL=$(terraform output -raw ingest_url)
export CHAT_URL=$(terraform output -raw chat_url)

# Test all health endpoints
echo "Master Agent:"
curl -s $MASTER_URL/health | jq .

echo "Pub/Sub:"
curl -s $PUBSUB_URL/health | jq .

echo "Ingest Agent:"
curl -s $INGEST_URL/health | jq .

echo "Chat Agent:"
curl -s $CHAT_URL/health | jq .
```

---

**See POSTMAN_TESTING_GUIDE.md for detailed examples!**
