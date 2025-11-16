# Unified Agentic System - Single Cloud Run service with all 4 agents

resource "google_cloud_run_service" "agentic_system" {
  name     = "agentic-system"
  location = var.region

  template {
    spec {
      service_account_name = var.cloud_run_service_account

      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repo}/agentic-system:latest"

        ports {
          container_port = 8000 # Master Agent port (exposed externally)
        }

        resources {
          limits = {
            cpu    = "2000m" # 2 CPUs shared by all services
            memory = "4Gi"   # 4GB shared by all services
          }
        }

        # All configuration fetched from Secret Manager at runtime
        # Secrets are mounted as environment variables
        env {
          name = "DATABASE_CREDENTIALS"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.database_credentials.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name = "API_KEYS"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.api_keys.secret_id
              key  = "latest"
            }
          }
        }
      }

      # Timeout for LLM processing
      timeout_seconds = 300 # 5 minutes
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale"  = "10" # Max 10 instances
        "autoscaling.knative.dev/minScale"  = "1"  # Always 1 instance running (warm start)
        "run.googleapis.com/cpu-throttling" = "true"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_project_service.run,
    google_artifact_registry_repository.agents,
    google_secret_manager_secret_version.database_credentials,
    google_secret_manager_secret_version.api_keys,
    google_secret_manager_secret_iam_member.database_credentials_access,
    google_secret_manager_secret_iam_member.api_keys_access
  ]
}

# Allow public access to the service
resource "google_cloud_run_service_iam_member" "agentic_system_public" {
  service  = google_cloud_run_service.agentic_system.name
  location = google_cloud_run_service.agentic_system.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
