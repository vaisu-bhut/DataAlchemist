# Cloud Run Deployment Checklist

## Before Deployment

### 1. GCP Setup
- [ ] GCP account created
- [ ] Billing enabled
- [ ] Project created
- [ ] gcloud CLI installed
- [ ] Logged in: `gcloud auth login`
- [ ] Project set: `gcloud config set project PROJECT_ID`

### 2. Prerequisites
- [ ] Neo4j Aura database created
- [ ] Neo4j credentials ready
- [ ] Gemini API key obtained
- [ ] Docker installed (for local testing)

### 3. Enable APIs
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

## Deployment Steps

### Option A: Automated (Recommended)

```bash
# 1. Setup secrets
chmod +x setup-secrets.sh
./setup-secrets.sh

# 2. Deploy all agents
chmod +x deploy.sh
./deploy.sh
```

### Option B: Manual

Follow `DEPLOY_TO_CLOUD_RUN.md` step by step.

## After Deployment

### 1. Verify Services
- [ ] Check all services are running:
```bash
gcloud run services list
```

- [ ] Test health endpoints:
```bash
MASTER_URL=$(gcloud run services describe master-agent --format 'value(status.url)')
curl $MASTER_URL/health
```

### 2. Test Functionality
- [ ] Test ingest endpoint
- [ ] Test chat endpoint
- [ ] Check logs for errors

### 3. Monitor
- [ ] Set up Cloud Monitoring alerts
- [ ] Check billing dashboard
- [ ] Review logs regularly

## Cost Optimization

- [ ] Set min-instances to 0 for ingest (scales to zero)
- [ ] Enable CPU throttling
- [ ] Set appropriate memory limits
- [ ] Configure max-instances based on expected load

## Security

- [ ] Review IAM permissions
- [ ] Verify secrets are not exposed
- [ ] Consider adding authentication
- [ ] Set up VPC connector if needed

## Troubleshooting

### Service won't start
```bash
gcloud run services logs read SERVICE_NAME --limit 100
```

### Secrets not accessible
```bash
# Grant access to secrets
gcloud secrets add-iam-policy-binding SECRET_NAME \
  --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

### High costs
- Check instance counts
- Review memory allocation
- Enable scale-to-zero for ingest
- Check request logs

## Maintenance

### Update an agent
```bash
cd agents/AGENT_NAME
gcloud builds submit --tag gcr.io/PROJECT_ID/AGENT_NAME
gcloud run deploy AGENT_NAME --image gcr.io/PROJECT_ID/AGENT_NAME
```

### View logs
```bash
gcloud run services logs read AGENT_NAME --limit 50
```

### Rollback
```bash
gcloud run revisions list --service AGENT_NAME
gcloud run services update-traffic AGENT_NAME --to-revisions REVISION=100
```

## Success Criteria

✅ All 4 services deployed
✅ Health checks passing
✅ Can ingest conversations
✅ Can query knowledge
✅ Logs show no errors
✅ Costs within budget

---

**Ready to deploy!** Follow the checklist and you'll be live in ~15 minutes.
