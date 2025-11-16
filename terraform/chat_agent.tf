# Chat Agent - Conversational worker

resource "google_cloud_run_service" "chat" {
  name     = "chat-agent"
  location = var.region

  template {
    spec {
      service_account_name = var.cloud_run_service_account

      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repo}/chat-agent:latest"

        ports {
          container_port = 8003
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "1Gi"
          }
        }

        env {
          name  = "PUBSUB_URL"
          value = google_cloud_run_service.pubsub.status[0].url
        }

        env {
          name  = "GEMINI_MODEL_NAME"
          value = var.gemini_model_name
        }

        env {
          name  = "GEMINI_EMBEDDING_MODEL"
          value = var.gemini_embedding_model
        }

        env {
          name  = "CHUNK_SIZE"
          value = var.chunk_size
        }

        env {
          name  = "SIMILARITY_THRESHOLD"
          value = var.similarity_threshold
        }

        env {
          name  = "CONFIDENCE_THRESHOLD"
          value = var.confidence_threshold
        }

        env {
          name  = "MAX_RETRIEVAL_RESULTS"
          value = var.max_retrieval_results
        }

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

      timeout_seconds = 60
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "20"
        "autoscaling.knative.dev/minScale" = "1"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_cloud_run_service.pubsub,
    google_secret_manager_secret_version.database_credentials,
    google_secret_manager_secret_version.api_keys,
    google_secret_manager_secret_iam_member.database_credentials_access,
    google_secret_manager_secret_iam_member.api_keys_access
  ]
}

resource "google_cloud_run_service_iam_member" "chat_public" {
  service  = google_cloud_run_service.chat.name
  location = google_cloud_run_service.chat.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
