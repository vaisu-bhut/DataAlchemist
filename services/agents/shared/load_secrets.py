"""
Load JSON secrets on startup - Import this first in main.py
"""
import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Load database credentials
db_creds_json = os.getenv("DATABASE_CREDENTIALS")
if db_creds_json:
    try:
        db_creds = json.loads(db_creds_json)
        # Use lowercase to match pydantic Settings field names
        os.environ["neo4j_uri"] = db_creds.get("neo4j_uri", os.getenv("neo4j_uri", ""))
        os.environ["neo4j_user"] = db_creds.get("neo4j_user", os.getenv("neo4j_user", "neo4j"))
        os.environ["neo4j_password"] = db_creds.get("neo4j_password", os.getenv("neo4j_password", ""))
        logger.info("✅ Database credentials loaded from JSON")
    except json.JSONDecodeError as e:
        logger.warning(f"⚠️  Failed to parse DATABASE_CREDENTIALS: {e}")
else:
    logger.info("ℹ️  Using individual environment variables for database")

# Load API keys
api_keys_json = os.getenv("API_KEYS")
if api_keys_json:
    try:
        api_keys = json.loads(api_keys_json)
        # Use lowercase to match pydantic Settings field names
        os.environ["gemini_api_key"] = api_keys.get("gemini_api_key", os.getenv("gemini_api_key", ""))
        os.environ["gemini_model_name"] = api_keys.get("gemini_model_name", os.getenv("gemini_model_name", "gemini-2.5-pro"))
        os.environ["gemini_embedding_model"] = api_keys.get("gemini_embedding_model", os.getenv("gemini_embedding_model", "models/text-embedding-004"))
        os.environ["secret_key"] = api_keys.get("app_secret_key", os.getenv("secret_key", ""))
        logger.info("✅ API keys loaded from JSON")
    except json.JSONDecodeError as e:
        logger.warning(f"⚠️  Failed to parse API_KEYS: {e}")
else:
    logger.info("ℹ️  Using individual environment variables for API keys")

logger.info("🚀 Secrets loaded successfully")
