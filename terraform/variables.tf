# Project Configuration
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Run services"
  type        = string
  default     = "us-central1"
}

variable "artifact_registry_repo" {
  description = "Artifact Registry repository name"
  type        = string
  default     = "agentic-system"
}

# Neo4j Configuration
variable "neo4j_uri" {
  description = "Neo4j connection URI"
  type        = string
  sensitive   = true
}

variable "neo4j_user" {
  description = "Neo4j username"
  type        = string
  default     = "neo4j"
  sensitive   = true
}

variable "neo4j_password" {
  description = "Neo4j password"
  type        = string
  sensitive   = true
}

# Gemini Configuration
variable "gemini_api_key" {
  description = "Google Gemini API key"
  type        = string
  sensitive   = true
}

variable "gemini_model_name" {
  description = "Gemini model name"
  type        = string
  default     = "gemini-2.0-flash-exp"
}

variable "gemini_embedding_model" {
  description = "Gemini embedding model"
  type        = string
  default     = "models/text-embedding-004"
}

# Application Configuration
variable "secret_key" {
  description = "Application secret key for encryption"
  type        = string
  sensitive   = true
}

variable "chunk_size" {
  description = "Text chunk size for processing"
  type        = string
  default     = "2000"
}

variable "similarity_threshold" {
  description = "Similarity threshold for matching"
  type        = string
  default     = "0.85"
}

variable "confidence_threshold" {
  description = "Confidence threshold for responses"
  type        = string
  default     = "0.7"
}

variable "max_retrieval_results" {
  description = "Maximum number of retrieval results"
  type        = string
  default     = "10"
}

# Cloud Run Service Account
variable "cloud_run_service_account" {
  description = "Service account email for Cloud Run services"
  type        = string
  default     = "cloud-run-sa@dataalchemist-476923.iam.gserviceaccount.com"
}
