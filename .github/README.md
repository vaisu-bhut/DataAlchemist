# GitHub Actions Setup

This repository uses GitHub Actions for CI/CD with the following workflows:

## Workflows

### PR Check (`pr-check.yml`)
- Triggers on PRs to `main` or `staging` branches
- Validates Terraform templates
- Tests Docker build process
- Validates Python dependencies

### Build and Deploy (`deploy.yml`)
- Triggers on push/merge to `main` or `staging` branches
- Validates Terraform templates
- Builds Docker image
- Pushes to GCP Artifact Registry

## Required GitHub Secrets

Configure these secrets in your repository settings:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `GCP_PROJECT_ID` | Your GCP project ID | `my-project-123` |
| `GAR_LOCATION` | Artifact Registry location | `us-central1` |
| `GAR_REPOSITORY` | Artifact Registry repository name | `my-app-repo` |
| `SERVICE_NAME` | Service/image name | `my-service` |
| `GCP_SA_KEY` | GCP Service Account JSON key | `{"type": "service_account", ...}` |

## GCP Service Account Permissions

The service account used in `GCP_SA_KEY` needs these IAM roles:
- `roles/artifactregistry.writer`
- `roles/storage.admin` (if using GCS for Terraform state)

## Setup Instructions

1. Create a GCP Artifact Registry repository:
   ```bash
   gcloud artifacts repositories create [REPOSITORY_NAME] \
     --repository-format=docker \
     --location=[LOCATION]
   ```

2. Create a service account and download the JSON key:
   ```bash
   gcloud iam service-accounts create github-actions
   gcloud iam service-accounts keys create key.json \
     --iam-account=github-actions@[PROJECT_ID].iam.gserviceaccount.com
   ```

3. Grant necessary permissions to the service account:
   ```bash
   gcloud projects add-iam-policy-binding [PROJECT_ID] \
     --member="serviceAccount:github-actions@[PROJECT_ID].iam.gserviceaccount.com" \
     --role="roles/artifactregistry.writer"
   ```

4. Add the secrets to your GitHub repository settings.