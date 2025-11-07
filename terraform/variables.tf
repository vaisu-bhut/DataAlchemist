variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "service_name" {
  description = "Name of the Cloud Run service"
  type        = string
}

variable "gar_location" {
  description = "Google Artifact Registry location"
  type        = string
}

variable "repository" {
  description = "Artifact Registry repository name"
  type        = string
}

variable "neo4j_uri" {
  description = "Neo4j database URI"
  type        = string
}

variable "neo4j_user" {
  description = "Neo4j username"
  type        = string
}

variable "neo4j_password" {
  description = "Neo4j password"
  type        = string
  sensitive   = true
}

variable "gemini_api_key" {
  description = "Gemini API key"
  type        = string
  sensitive   = true
}

variable "gemini_model_name" {
  description = "Gemini model name"
  type        = string
}

variable "gemini_embedding_model" {
  description = "Gemini embedding model"
  type        = string
}

variable "secret_key" {
  description = "Application secret key"
  type        = string
  sensitive   = true
}

variable "chunk_size" {
  description = "Text chunk size"
  type        = string
}

variable "similarity_threshold" {
  description = "Similarity threshold"
  type        = string
}

variable "confidence_threshold" {
  description = "Confidence threshold"
  type        = string
}

variable "max_retrieval_results" {
  description = "Maximum retrieval results"
  type        = string
}
