# Terraform outputs

output "pubsub_url" {
  description = "Pub/Sub service URL"
  value       = google_cloud_run_service.pubsub.status[0].url
}

output "master_url" {
  description = "Master Agent URL (main API endpoint)"
  value       = google_cloud_run_service.master.status[0].url
}

output "ingest_url" {
  description = "Ingest Agent URL"
  value       = google_cloud_run_service.ingest.status[0].url
}

output "chat_url" {
  description = "Chat Agent URL"
  value       = google_cloud_run_service.chat.status[0].url
}

output "api_endpoint" {
  description = "Main API endpoint to use"
  value       = google_cloud_run_service.master.status[0].url
}

output "artifact_registry_repo" {
  description = "Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repo}"
}
