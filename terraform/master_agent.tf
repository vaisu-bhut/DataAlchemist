# Master Agent - Orchestrator and API Gateway

resource "google_cloud_run_service" "master" {
  name     = "master-agent"
  location = var.region

  template {
    spec {
      service_account_name = var.cloud_run_service_account

      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repo}/master-agent:latest"

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
          name  = "PUBSUB_URL"
          value = google_cloud_run_service.pubsub.status[0].url
        }
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "5"
        "autoscaling.knative.dev/minScale" = "1"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_cloud_run_service.pubsub]
}

resource "google_cloud_run_service_iam_member" "master_public" {
  service  = google_cloud_run_service.master.name
  location = google_cloud_run_service.master.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
