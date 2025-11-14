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
        os.environ["NEO4J_URI"] = db_creds.get("neo4j_uri", os.getenv("NEO4J_URI", ""))
        os.environ["NEO4J_USER"] = db_creds.get("neo4j_user", os.getenv("NEO4J_USER", "neo4j"))
        os.environ["NEO4J_PASSWORD"] = db_creds.get("neo4j_password", os.getenv("NEO4J_PASSWORD", ""))
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
        os.environ["GEMINI_API_KEY"] = api_keys.get("gemini_api_key", os.getenv("GEMINI_API_KEY", ""))
        os.environ["GEMINI_MODEL_NAME"] = api_keys.get("gemini_model_name", os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-pro"))
        os.environ["GEMINI_EMBEDDING_MODEL"] = api_keys.get("gemini_embedding_model", os.getenv("GEMINI_EMBEDDING_MODEL", "models/text-embedding-004"))
        os.environ["SECRET_KEY"] = api_keys.get("app_secret_key", os.getenv("SECRET_KEY", ""))
        logger.info("✅ API keys loaded from JSON")
    except json.JSONDecodeError as e:
        logger.warning(f"⚠️  Failed to parse API_KEYS: {e}")
else:
    logger.info("ℹ️  Using individual environment variables for API keys")

logger.info("🚀 Secrets loaded successfully")
