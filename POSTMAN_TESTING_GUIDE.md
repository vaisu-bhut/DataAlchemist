# Postman Testing Guide - Agentic Workflow System

## 🚀 Get Your API URL

First, get your Master Agent URL from Terraform:

```bash
cd terraform
terraform output master_url
```

Example: `https://master-agent-xxx-ue.a.run.app`

## 📋 Postman Collection Setup

### 1. Create New Collection
1. Open Postman
2. Click **"New"** → **"Collection"**
3. Name it: **"Agentic Workflow API"**

### 2. Set Collection Variable
1. Click on your collection
2. Go to **"Variables"** tab
3. Add variable:
   - **Variable:** `base_url`
   - **Initial Value:** `https://master-agent-xxx-ue.a.run.app`
   - **Current Value:** (same as initial)

## 🧪 Test Requests

### Test 1: Health Check

**Request:**
- **Method:** `GET`
- **URL:** `{{base_url}}/health`

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "master-agent-langgraph",
  "version": "2.0.0"
}
```

---

### Test 2: Root Endpoint

**Request:**
- **Method:** `GET`
- **URL:** `{{base_url}}/`

**Expected Response:**
```json
{
  "message": "Master Agent with LangGraph",
  "status": "running",
  "version": "2.0.0"
}
```

---

### Test 3: Ingest Conversation

**Request:**
- **Method:** `POST`
- **URL:** `{{base_url}}/api/v1/ingest`
- **Headers:**
  - `Content-Type: application/json`
- **Body (raw JSON):**

```json
{
  "conversations": [
    {
      "conversation_id": "conv_001",
      "customer_id": "customer_123",
      "agent_id": "agent_456",
      "messages": [
        {
          "role": "customer",
          "content": "I cannot log into my account. It says my password is incorrect."
        },
        {
          "role": "agent",
          "content": "I understand you're having trouble logging in. Let me help you reset your password. First, please go to the login page and click 'Forgot Password'."
        },
        {
          "role": "customer",
          "content": "Okay, I clicked it. Now what?"
        },
        {
          "role": "agent",
          "content": "Great! You should receive an email with a password reset link. Please check your inbox and spam folder. The email will arrive within 5 minutes."
        },
        {
          "role": "customer",
          "content": "Got it! I received the email and reset my password. I can log in now. Thank you!"
        },
        {
          "role": "agent",
          "content": "Wonderful! I'm glad we could resolve this. Is there anything else I can help you with today?"
        }
      ]
    }
  ]
}
```

**Expected Response:**
```json
{
  "success": true,
  "processed_count": 1,
  "failed_count": 0,
  "errors": null
}
```

**Note:** This may take 30-60 seconds as it processes through LLM.

---

### Test 4: Chat Query (After Ingestion)

**Request:**
- **Method:** `POST`
- **URL:** `{{base_url}}/api/v1/chat`
- **Headers:**
  - `Content-Type: application/json`
- **Body (raw JSON):**

```json
{
  "query": "How do I reset my password?",
  "customer_id": "customer_123"
}
```

**Expected Response:**
```json
{
  "answer": "To reset your password, go to the login page and click 'Forgot Password'. You'll receive an email with a password reset link within 5 minutes. Check both your inbox and spam folder.",
  "sources": [
    {
      "source_id": "...",
      "conversation_id": "conv_001",
      "snippet": "...",
      "relevance_score": 0.95
    }
  ],
  "confidence": 0.92
}
```

---

### Test 5: Multiple Conversations

**Request:**
- **Method:** `POST`
- **URL:** `{{base_url}}/api/v1/ingest`
- **Body (raw JSON):**

```json
{
  "conversations": [
    {
      "conversation_id": "conv_002",
      "customer_id": "customer_456",
      "agent_id": "agent_789",
      "messages": [
        {
          "role": "customer",
          "content": "My order hasn't arrived yet. It's been 2 weeks."
        },
        {
          "role": "agent",
          "content": "I apologize for the delay. Let me check your order status. Can you provide your order number?"
        },
        {
          "role": "customer",
          "content": "It's ORDER-12345"
        },
        {
          "role": "agent",
          "content": "Thank you. I see your order is currently in transit. It should arrive within 2-3 business days. I'll send you a tracking link via email."
        }
      ]
    },
    {
      "conversation_id": "conv_003",
      "customer_id": "customer_789",
      "agent_id": "agent_456",
      "messages": [
        {
          "role": "customer",
          "content": "How do I cancel my subscription?"
        },
        {
          "role": "agent",
          "content": "To cancel your subscription, go to Account Settings > Subscriptions > Cancel. You can also contact us and we'll cancel it for you."
        },
        {
          "role": "customer",
          "content": "Will I get a refund?"
        },
        {
          "role": "agent",
          "content": "If you cancel within 30 days of your last payment, you'll receive a prorated refund. After 30 days, the cancellation takes effect at the end of your billing cycle."
        }
      ]
    }
  ]
}
```

---

### Test 6: Different Chat Queries

Try these queries after ingesting conversations:

**Query 1: Order Status**
```json
{
  "query": "Where is my order?",
  "customer_id": "customer_456"
}
```

**Query 2: Subscription Cancellation**
```json
{
  "query": "How can I cancel my subscription?",
  "customer_id": "customer_789"
}
```

**Query 3: Refund Policy**
```json
{
  "query": "Can I get a refund if I cancel?",
  "customer_id": "customer_789"
}
```

**Query 4: General Question**
```json
{
  "query": "What are your business hours?",
  "customer_id": "customer_999"
}
```

## 📊 Testing Workflow

### Complete Test Flow:

1. **Health Check** → Verify all services are running
2. **Ingest Conversation** → Add knowledge to the system
3. **Wait 30-60 seconds** → Let processing complete
4. **Chat Query** → Test retrieval and response generation
5. **Verify Response** → Check answer quality and sources

### Expected Timing:
- **Health Check:** < 1 second
- **Ingest:** 30-60 seconds (LLM processing)
- **Chat:** 5-10 seconds (retrieval + LLM synthesis)

## 🔍 Monitoring Responses

### Successful Ingest Response:
```json
{
  "success": true,
  "processed_count": 1,
  "failed_count": 0,
  "errors": null
}
```

### Failed Ingest Response:
```json
{
  "success": false,
  "processed_count": 0,
  "failed_count": 1,
  "errors": ["Error message here"]
}
```

### Good Chat Response:
```json
{
  "answer": "Detailed answer based on knowledge base",
  "sources": [...],
  "confidence": 0.85  // High confidence
}
```

### Low Confidence Response:
```json
{
  "answer": "I don't have enough information...",
  "sources": [],
  "confidence": 0.0  // No relevant knowledge found
}
```

## 🐛 Troubleshooting

### Error: Connection Timeout
**Cause:** Service is cold starting
**Fix:** Wait 10-15 seconds and retry

### Error: 500 Internal Server Error
**Cause:** Check logs
**Fix:** 
```bash
gcloud run services logs read master-agent --region=us-east1 --limit=50
```

### Error: No relevant knowledge found
**Cause:** No conversations ingested yet
**Fix:** Run ingest request first

### Error: Invalid request format
**Cause:** Missing required fields
**Fix:** Check JSON structure matches examples above

## 📝 Postman Collection JSON

Save this as a file and import into Postman:

```json
{
  "info": {
    "name": "Agentic Workflow API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "https://master-agent-xxx-ue.a.run.app",
      "type": "string"
    }
  ],
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/health",
          "host": ["{{base_url}}"],
          "path": ["health"]
        }
      }
    },
    {
      "name": "Ingest Conversation",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"conversations\": [\n    {\n      \"conversation_id\": \"conv_001\",\n      \"customer_id\": \"customer_123\",\n      \"agent_id\": \"agent_456\",\n      \"messages\": [\n        {\n          \"role\": \"customer\",\n          \"content\": \"I cannot log into my account.\"\n        },\n        {\n          \"role\": \"agent\",\n          \"content\": \"Let me help you reset your password.\"\n        }\n      ]\n    }\n  ]\n}"
        },
        "url": {
          "raw": "{{base_url}}/api/v1/ingest",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "ingest"]
        }
      }
    },
    {
      "name": "Chat Query",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"query\": \"How do I reset my password?\",\n  \"customer_id\": \"customer_123\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/api/v1/chat",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "chat"]
        }
      }
    }
  ]
}
```

## 🎯 Success Criteria

Your system is working correctly if:
- ✅ Health check returns 200 OK
- ✅ Ingest processes conversations successfully
- ✅ Chat returns relevant answers with sources
- ✅ Confidence scores are > 0.7 for known topics
- ✅ Response times are reasonable (< 60s for ingest, < 10s for chat)

## 📈 Advanced Testing

### Load Testing
Use Postman Runner to test multiple requests:
1. Create a collection
2. Click **"Run"**
3. Set iterations: 10
4. Set delay: 5000ms
5. Run collection

### Performance Monitoring
Check response times in Postman:
- **Tests** tab → Add assertion:
```javascript
pm.test("Response time is less than 10s", function () {
    pm.expect(pm.response.responseTime).to.be.below(10000);
});
```

---

**Happy Testing!** 🚀

Your agentic workflow system is now fully operational!
