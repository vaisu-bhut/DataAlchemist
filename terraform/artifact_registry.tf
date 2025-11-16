# Artifact Registry for container images

resource "google_artifact_registry_repository" "agents" {
  location      = var.region
  repository_id = var.artifact_registry_repo
  description   = "Docker repository for agentic workflow containers"
  format        = "DOCKER"

  depends_on = [google_project_service.artifactregistry]
}
