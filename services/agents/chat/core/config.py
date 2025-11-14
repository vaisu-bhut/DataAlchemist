import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Neo4j Configuration
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    
    # Gemini Configuration
    gemini_api_key: str
    gemini_model_name: str
    gemini_embedding_model: str
    
    # Application Configuration
    chunk_size: int
    similarity_threshold: float
    confidence_threshold: float
    max_retrieval_results: int
    
    # Security
    secret_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()