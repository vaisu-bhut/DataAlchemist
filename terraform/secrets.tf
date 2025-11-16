# Secret Manager secrets - Grouped by purpose

# Database Credentials (Neo4j)
resource "google_secret_manager_secret" "database_credentials" {
  secret_id = "database-credentials"
  replication {
    auto {}
  }
  depends_on = [google_project_service.secretmanager]
}

resource "google_secret_manager_secret_version" "database_credentials" {
  secret = google_secret_manager_secret.database_credentials.id
  secret_data = jsonencode({
    neo4j_uri      = var.neo4j_uri
    neo4j_user     = var.neo4j_user
    neo4j_password = var.neo4j_password
  })
}

# API Keys (Gemini and Application)
resource "google_secret_manager_secret" "api_keys" {
  secret_id = "api-keys"
  replication {
    auto {}
  }
  depends_on = [google_project_service.secretmanager]
}

resource "google_secret_manager_secret_version" "api_keys" {
  secret = google_secret_manager_secret.api_keys.id
  secret_data = jsonencode({
    gemini_api_key         = var.gemini_api_key
    gemini_model_name      = var.gemini_model_name
    gemini_embedding_model = var.gemini_embedding_model
    app_secret_key         = var.secret_key
  })
}

# Grant Cloud Run service account access to secrets
resource "google_secret_manager_secret_iam_member" "database_credentials_access" {
  secret_id = google_secret_manager_secret.database_credentials.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.cloud_run_service_account}"

  depends_on = [google_secret_manager_secret.database_credentials]
}

resource "google_secret_manager_secret_iam_member" "api_keys_access" {
  secret_id = google_secret_manager_secret.api_keys.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.cloud_run_service_account}"

  depends_on = [google_secret_manager_secret.api_keys]
}
