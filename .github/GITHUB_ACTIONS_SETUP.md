# GitHub Actions Service Account Setup

## Service Account

**Email:** `github-actions@dataalchemist-476923.iam.gserviceaccount.com`

## Required Roles

The GitHub Actions service account needs these roles to build and deploy:

### 1. Artifact Registry Administrator
**Purpose:** Create repositories and push container images

```bash
gcloud projects add-iam-policy-binding dataalchemist-476923 \
  --member="serviceAccount:github-actions@dataalchemist-476923.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"
```

### 2. Cloud Run Admin
**Purpose:** Deploy Cloud Run services

```bash
gcloud projects add-iam-policy-binding dataalchemist-476923 \
  --member="serviceAccount:github-actions@dataalchemist-476923.iam.gserviceaccount.com" \
  --role="roles/run.admin"
```

### 3. Service Account User
**Purpose:** Allow Cloud Run to use service accounts

```bash
gcloud projects add-iam-policy-binding dataalchemist-476923 \
  --member="serviceAccount:github-actions@dataalchemist-476923.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

### 4. Secret Manager Admin
**Purpose:** Create and manage secrets

```bash
gcloud projects add-iam-policy-binding dataalchemist-476923 \
  --member="serviceAccount:github-actions@dataalchemist-476923.iam.gserviceaccount.com" \
  --role="roles/secretmanager.admin"
```

## Quick Setup Script

```bash
#!/bin/bash

PROJECT_ID="dataalchemist-476923"
SA_EMAIL="github-actions@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Adding roles to GitHub Actions service account..."

# Artifact Registry Administrator
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/artifactregistry.admin"

# Cloud Run Admin
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

# Service Account User
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

# Secret Manager Admin
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.admin"

echo "✅ All roles added!"
```

## Verify Roles

```bash
gcloud projects get-iam-policy dataalchemist-476923 \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:github-actions@dataalchemist-476923.iam.gserviceaccount.com"
```

Should show:
- `roles/artifactregistry.admin`
- `roles/run.admin`
- `roles/iam.serviceAccountUser`
- `roles/secretmanager.admin`

## GitHub Secrets

Make sure these secrets are set in your GitHub repository:

| Secret Name | Value |
|-------------|-------|
| `GCP_PROJECT_ID` | `dataalchemist-476923` |
| `GCP_SA_KEY` | Service account JSON key |
| `NEO4J_URI` | Your Neo4j connection string |
| `NEO4J_USER` | `neo4j` |
| `NEO4J_PASSWORD` | Your Neo4j password |
| `GEMINI_API_KEY` | Your Gemini API key |
| `APP_SECRET_KEY` | Random secret key |

### Get Service Account Key

```bash
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions@dataalchemist-476923.iam.gserviceaccount.com

# Copy contents to GitHub secret GCP_SA_KEY
cat github-actions-key.json
```

## Workflow Overview

The GitHub Actions workflow:

1. **Authenticates** using service account key
2. **Configures** Docker for Artifact Registry
3. **Verifies** Artifact Registry repository exists
4. **Builds** 4 container images
5. **Pushes** images to Artifact Registry
6. **Runs** Terraform to deploy Cloud Run services
7. **Tests** health endpoints

## Troubleshooting

### Permission Denied Error

```
ERROR: Permission 'artifactregistry.repositories.create' denied
```

**Fix:** Add Artifact Registry Administrator role (see above)

### Authentication Failed

```
ERROR: (gcloud.auth.activate-service-account) Invalid credentials
```

**Fix:** Regenerate service account key and update `GCP_SA_KEY` secret

### Terraform Apply Failed

```
ERROR: Error creating Service: Container image not found
```

**Fix:** Ensure images were built and pushed successfully in previous step

## Testing

After adding roles, test the workflow:

```bash
# Trigger workflow manually
git commit --allow-empty -m "Test GitHub Actions"
git push origin main
```

Check workflow at: `https://github.com/YOUR_USERNAME/YOUR_REPO/actions`

---

**After adding all roles, GitHub Actions will work!** 🚀
