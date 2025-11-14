"""
Helper to load and parse JSON secrets from environment variables
"""
import os
import json
import logging

logger = logging.getLogger(__name__)


def load_secrets():
    """
    Load JSON secrets from environment variables and set individual env vars
    This allows existing code to work without changes
    """
    # Load database credentials
    db_creds_json = os.getenv("DATABASE_CREDENTIALS")
    if db_creds_json:
        try:
            db_creds = json.loads(db_creds_json)
            os.environ["NEO4J_URI"] = db_creds.get("neo4j_uri", "")
            os.environ["NEO4J_USER"] = db_creds.get("neo4j_user", "neo4j")
            os.environ["NEO4J_PASSWORD"] = db_creds.get("neo4j_password", "")
            logger.info("✅ Database credentials loaded from JSON secret")
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse DATABASE_CREDENTIALS JSON: {e}")
    
    # Load API keys
    api_keys_json = os.getenv("API_KEYS")
    if api_keys_json:
        try:
            api_keys = json.loads(api_keys_json)
            os.environ["GEMINI_API_KEY"] = api_keys.get("gemini_api_key", "")
            os.environ["GEMINI_MODEL_NAME"] = api_keys.get("gemini_model_name", "gemini-2.5-pro")
            os.environ["GEMINI_EMBEDDING_MODEL"] = api_keys.get("gemini_embedding_model", "models/text-embedding-004")
            os.environ["SECRET_KEY"] = api_keys.get("app_secret_key", "")
            logger.info("✅ API keys loaded from JSON secret")
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse API_KEYS JSON: {e}")


# Auto-load on import
load_secrets()
