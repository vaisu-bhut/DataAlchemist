# Cloud Run service
resource "google_cloud_run_service" "main" {
  name     = var.service_name
  location = var.region

  template {
    spec {
      service_account_name = "cloud-run-sa@${var.project_id}.iam.gserviceaccount.com"

      containers {
        image = "${var.gar_location}-docker.pkg.dev/${var.project_id}/${var.repository}/${var.service_name}:latest"

        ports {
          container_port = 8000
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }
        env {
          name  = "NEO4J_URI"
          value = var.neo4j_uri
        }
        env {
          name  = "NEO4J_USER"
          value = var.neo4j_user
        }
        env {
          name  = "NEO4J_PASSWORD"
          value = var.neo4j_password
        }
        env {
          name  = "GEMINI_API_KEY"
          value = var.gemini_api_key
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
          name  = "SECRET_KEY"
          value = var.secret_key
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

        startup_probe {
          http_get {
            path = "/health"
            port = 8000
          }
          initial_delay_seconds = 30
          timeout_seconds       = 10
          period_seconds        = 10
          failure_threshold     = 3
        }

        liveness_probe {
          http_get {
            path = "/health"
            port = 8000
          }
          initial_delay_seconds = 30
          timeout_seconds       = 5
          period_seconds        = 30
        }
      }
    }

    metadata {
      annotations = {
        # Scaling configuration
        "autoscaling.knative.dev/maxScale"          = "10"
        "autoscaling.knative.dev/minScale"          = "1"
        "autoscaling.knative.dev/targetUtilization" = "70" # Scale up at 70% CPU
        "run.googleapis.com/cpu-throttling"         = "false"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Allow unauthenticated access
resource "google_cloud_run_service_iam_member" "public" {
  service  = google_cloud_run_service.main.name
  location = google_cloud_run_service.main.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Output the service URL
output "service_url" {
  description = "The URL of the deployed Cloud Run service"
  value       = google_cloud_run_service.main.status[0].url
}
