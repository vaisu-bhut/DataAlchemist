# Pub/Sub Service - Message routing for agent communication

resource "google_cloud_run_service" "pubsub" {
  name     = "pubsub"
  location = var.region

  template {
    spec {
      service_account_name = var.cloud_run_service_account

      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repo}/pubsub:latest"

        ports {
          container_port = 8001
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "256Mi"
          }
        }
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "3"
        "autoscaling.knative.dev/minScale" = "1"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_project_service.run]
}

resource "google_cloud_run_service_iam_member" "pubsub_public" {
  service  = google_cloud_run_service.pubsub.name
  location = google_cloud_run_service.pubsub.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
