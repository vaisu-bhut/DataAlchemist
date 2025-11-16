# Terraform outputs

output "service_url" {
  description = "Unified Agentic System URL (main API endpoint)"
  value       = google_cloud_run_service.agentic_system.status[0].url
}

output "api_endpoint" {
  description = "Main API endpoint to use for ingest and chat"
  value       = google_cloud_run_service.agentic_system.status[0].url
}

output "artifact_registry_repo" {
  description = "Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repo}"
}

output "service_name" {
  description = "Cloud Run service name"
  value       = google_cloud_run_service.agentic_system.name
}

output "service_location" {
  description = "Cloud Run service location"
  value       = google_cloud_run_service.agentic_system.location
}

# Instructions for usage
output "usage_instructions" {
  description = "How to use the deployed service"
  value       = <<-EOT
    
    Unified Agentic System deployed successfully!
    
    Service URL: ${google_cloud_run_service.agentic_system.status[0].url}
    
    Test the service:
    
    # Health check
    curl ${google_cloud_run_service.agentic_system.status[0].url}/health
    
    # Ingest conversations
    curl -X POST ${google_cloud_run_service.agentic_system.status[0].url}/api/v1/ingest \
      -H "Content-Type: application/json" \
      -d '{"conversations": [...]}'
    
    # Chat query
    curl -X POST ${google_cloud_run_service.agentic_system.status[0].url}/api/v1/chat \
      -H "Content-Type: application/json" \
      -d '{"query": "How do I reset my password?"}'
    
    All 4 services running in one container:
    - Pub/Sub (internal port 8001)
    - Master Agent (exposed port 8000)
    - Ingest Agent (internal port 8002)
    - Chat Agent (internal port 8003)
  EOT
}
