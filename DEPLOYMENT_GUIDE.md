# Agentic Workflow System - Complete Deployment Guide

## 🎯 Overview

Multi-agent AI system with **LangChain**, **LangGraph**, and **LangSmith** deployed to Google Cloud Run using Terraform and GitHub Actions CI/CD.

## 🏗️ Architecture

```
GitHub Push → GitHub Actions → Build Images → Push to Registry
                                    ↓
                              Terraform Apply
                                    ↓
                    ┌───────────────┴───────────────┐
                    │                               │
            Pub/Sub Service                 Master Agent
                    │                        (API Gateway)
            ┌───────┴───────┐                      │
            │               │                      │
      Ingest Agent    Chat Agent                   │
            │               │                      │
            └───────┬───────┘                      │
                    │                              │
                Neo4j Database ←──────────────────┘
```

## 📦 What's Included

### Services (4 Cloud Run services)
- **Pub/Sub** - Message routing
- **Master Agent** - Orchestrator
- **Ingest Agent** - Data processing
- **Chat Agent** - Conversational

### Infrastructure as Code
- **Terraform** - Modular configuration
- **GitHub Actions** - CI/CD pipeline
- **Artifact Registry** - Container images
- **Secret Manager** - Credentials

## 🚀 Deployment Options

### Option 1: CI/CD (Recommended)

**Setup once:**
```bash
# 1. Add GitHub secrets
GCP_PROJECT_ID
GCP_SA_KEY
NEO4J_URI
NEO4J_USER
NEO4J_PASSWORD
GEMINI_API_KEY
APP_SECRET_KEY
```

**Deploy:**
```bash
git push origin main
```

GitHub Actions automatically builds and deploys!

### Option 2: Manual Deployment

```bash
# 1. Configure
cd terraform
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars

# 2. Deploy
terraform init
terraform plan
terraform apply
```

## 📁 Project Structure

```
.
├── services/
│   ├── agents/
│   │   ├── shared/          # Common utilities
│   │   ├── master/          # Orchestrator
│   │   ├── ingest/          # Data processor
│   │   └── chat/            # Conversational
│   ├── pubsub/              # Message router
│   └── [documentation]
├── terraform/
│   ├── main.tf              # Entry point
│   ├── apis.tf              # GCP APIs
│   ├── artifact_registry.tf # Container registry
│   ├── secrets.tf           # Secrets
│   ├── pubsub_service.tf    # Pub/Sub service
│   ├── master_agent.tf      # Master agent
│   ├── ingest_agent.tf      # Ingest agent
│   ├── chat_agent.tf        # Chat agent
│   ├── outputs.tf           # Outputs
│   ├── variables.tf         # Variables
│   └── provider.tf          # Provider
└── .github/workflows/
    └── deploy-agents.yml    # CI/CD
```

## 🔑 Key Features

✅ **Stateless Agents** - Scale infinitely
✅ **Pub/Sub Communication** - Decoupled messaging
✅ **LangGraph Workflows** - Visual state machines
✅ **Auto-scaling** - 0 to 1000+ req/sec
✅ **CI/CD** - Push to deploy
✅ **Modular Terraform** - Easy to customize

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| `terraform/README.md` | Terraform deployment |
| `services/AGENTS_README.md` | Agent system guide |
| `services/ARCHITECTURE.md` | System design |
| `services/QUICK_REFERENCE.md` | Command reference |

## 🎓 Quick Start

### 1. Prerequisites
- GCP account with billing
- Neo4j Aura database
- Gemini API key
- GitHub repository

### 2. Setup GitHub Secrets
Go to: `Settings → Secrets and variables → Actions`

Add:
- `GCP_PROJECT_ID`
- `GCP_SA_KEY` (service account JSON)
- `NEO4J_URI`
- `NEO4J_USER`
- `NEO4J_PASSWORD`
- `GEMINI_API_KEY`
- `APP_SECRET_KEY`

### 3. Deploy
```bash
git push origin main
```

### 4. Test
```bash
# Get URL from GitHub Actions output
curl https://master-agent-xxx.run.app/health
```

## 🔄 Update Workflow

1. **Make code changes**
2. **Commit and push**
3. **GitHub Actions builds and deploys**
4. **Services update automatically**

## 🗑️ Destroy

```bash
cd terraform
terraform destroy
```

## 💰 Cost

- **Development**: ~$10-20/month
- **Production**: ~$150-300/month
- Plus Neo4j and Gemini API

## 🆘 Support

- Check `terraform/README.md` for detailed instructions
- Review GitHub Actions logs for build issues
- Check Cloud Run logs for runtime issues

---

**Ready to deploy!** 🚀

**Next steps:**
1. Add GitHub secrets
2. Push to main
3. Monitor deployment
4. Test endpoints
