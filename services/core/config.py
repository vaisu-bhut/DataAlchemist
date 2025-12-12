"""
Configuration management with JSON secret support
"""

import os
import json
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with JSON secret parsing"""

    # Project settings
    project_id: str = "dataalchemist-476923"

    # Parse JSON secrets from environment
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._parse_json_secrets()

    def _parse_json_secrets(self):
        """Parse JSON secrets from environment variables"""
        # Parse database credentials
        db_creds_json = os.getenv("DATABASE_CREDENTIALS")
        if db_creds_json:
            try:
                db_creds = json.loads(db_creds_json)
                self.neo4j_uri = db_creds.get("neo4j_uri")
                self.neo4j_user = db_creds.get("neo4j_user")
                self.neo4j_password = db_creds.get("neo4j_password")
            except json.JSONDecodeError:
                pass

        # Parse API keys
        api_keys_json = os.getenv("API_KEYS")
        if api_keys_json:
            try:
                api_keys = json.loads(api_keys_json)
                self.gemini_api_key = api_keys.get("gemini_api_key")
                self.gemini_model_name = api_keys.get(
                    "gemini_model_name", "gemini-2.5-flash"
                )
                self.gemini_embedding_model = api_keys.get(
                    "gemini_embedding_model", "models/text-embedding-004"
                )
                self.secret_key = api_keys.get("app_secret_key")
            except json.JSONDecodeError:
                pass

    # Neo4j Configuration
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password")

    # Gemini Configuration
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model_name: str = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
    gemini_embedding_model: str = os.getenv(
        "GEMINI_EMBEDDING_MODEL", "models/text-embedding-004"
    )

    # Application Configuration
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "2000"))
    similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))
    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.4"))
    max_retrieval_results: int = int(os.getenv("MAX_RETRIEVAL_RESULTS", "10"))

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
