"""
Simple Ingest Agent - Processes conversations and stores in Neo4j
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
import httpx
import asyncio
import structlog
import os
import sys

# Add parent directories to path
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/agents/ingest')

# Load JSON secrets BEFORE importing config
import json
db_creds_json = os.getenv("DATABASE_CREDENTIALS")
if db_creds_json:
    try:
        db_creds = json.loads(db_creds_json)
        # Use lowercase to match pydantic Settings field names
        os.environ["neo4j_uri"] = db_creds.get("neo4j_uri", "")
        os.environ["neo4j_user"] = db_creds.get("neo4j_user", "neo4j")
        os.environ["neo4j_password"] = db_creds.get("neo4j_password", "")
    except: pass

api_keys_json = os.getenv("API_KEYS")
if api_keys_json:
    try:
        api_keys = json.loads(api_keys_json)
        # Use lowercase to match pydantic Settings field names
        os.environ["gemini_api_key"] = api_keys.get("gemini_api_key", "")
        os.environ["gemini_model_name"] = api_keys.get("gemini_model_name", "gemini-2.5-pro")
        os.environ["gemini_embedding_model"] = api_keys.get("gemini_embedding_model", "models/text-embedding-004")
        os.environ["secret_key"] = api_keys.get("app_secret_key", "")
    except: pass

# Set defaults (lowercase to match pydantic Settings)
os.environ.setdefault("chunk_size", "2000")
os.environ.setdefault("similarity_threshold", "0.85")
os.environ.setdefault("confidence_threshold", "0.7")
os.environ.setdefault("max_retrieval_results", "10")

logger = structlog.get_logger()

# Get PUBSUB_URL from environment or use default
PUBSUB_URL = os.getenv("PUBSUB_URL", "http://pubsub:8001")

# Import after secrets are loaded
from core.database import Neo4jConnection
from services.ingestion_service import IngestionService
from models.schemas import ConversationData

neo4j_conn = None
ingestion_service = None
polling_task = None

# Log configuration on startup
logger.info("Ingest Agent Configuration", pubsub_url=PUBSUB_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global neo4j_conn, ingestion_service, polling_task
    
    # Startup
    logger.info("Starting Ingest Agent")
    
    # Wait a bit for other services to be ready
    await asyncio.sleep(2)
    
    # Connect to Neo4j with retries (but don't fail startup)
    neo4j_conn = Neo4jConnection()
    for attempt in range(3):
        try:
            await neo4j_conn.connect()
            await neo4j_conn.initialize_schema()
            logger.info("✅ Connected to Neo4j and initialized schema")
            break
        except Exception as e:
            logger.warning(f"⚠️  Neo4j connection attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                await asyncio.sleep(3)
            else:
                logger.error("❌ Failed to connect to Neo4j after 3 attempts - service will start but may not process requests")
                # Don't raise - let service start anyway
                neo4j_conn = None
    
    # Initialize ingestion service (only if Neo4j connected)
    if neo4j_conn:
        ingestion_service = IngestionService(neo4j_conn)
    else:
        logger.warning("⚠️  Ingestion service not initialized - Neo4j connection failed")
    
    # Start polling for messages
    polling_task = asyncio.create_task(poll_for_requests())
    
    logger.info("Ingest agent ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Ingest Agent")
    if polling_task:
        polling_task.cancel()
    if neo4j_conn:
        await neo4j_conn.close()


app = FastAPI(title="Simple Ingest Agent", version="1.0.0", lifespan=lifespan)


async def poll_for_requests():
    """Poll pub/sub for ingest requests"""
    logger.info("Starting to poll for ingest requests")
    
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # Poll for messages
                response = await client.get(
                    f"{PUBSUB_URL}/poll/ingest.request",
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    message = data.get("message")
                    
                    if message:
                        logger.info("Received ingest request", 
                                   correlation_id=message.get("correlation_id"))
                        await process_request(message)
                
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Polling error", error=str(e))
                await asyncio.sleep(1)


async def process_request(message: dict):
    """Process an ingest request"""
    correlation_id = message.get("correlation_id")
    conversations_data = message.get("conversations", [])
    
    try:
        # Convert to ConversationData objects
        conversations = [
            ConversationData(**conv) 
            for conv in conversations_data
        ]
        
        # Process through ingestion service
        result = await ingestion_service.process_conversations(conversations)
        
        # Publish response
        response_message = {
            "correlation_id": correlation_id,
            "success": result.success,
            "processed_count": result.processed_count,
            "failed_count": result.failed_count,
            "errors": result.errors
        }
        
        logger.info("📤 Publishing response to pubsub", 
                   correlation_id=correlation_id,
                   topic="ingest.response",
                   message=response_message)
        
        async with httpx.AsyncClient() as client:
            publish_response = await client.post(
                f"{PUBSUB_URL}/publish",
                json={"topic": "ingest.response", "message": response_message},
                timeout=5.0
            )
            logger.info("✅ Response published successfully", 
                       correlation_id=correlation_id,
                       status_code=publish_response.status_code)
        
        logger.info("Ingest completed", 
                   correlation_id=correlation_id,
                   processed=result.processed_count)
        
    except Exception as e:
        logger.error("Processing failed", 
                    correlation_id=correlation_id,
                    error=str(e))
        
        # Publish error response
        error_message = {
            "correlation_id": correlation_id,
            "success": False,
            "processed_count": 0,
            "failed_count": len(conversations_data),
            "errors": [str(e)]
        }
        
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{PUBSUB_URL}/publish",
                json={"topic": "ingest.response", "message": error_message},
                timeout=5.0
            )


@app.get("/health")
async def health():
    db_healthy = False
    if neo4j_conn:
        try:
            db_healthy = await neo4j_conn.health_check()
        except:
            db_healthy = False
    
    return {
        "status": "healthy" if db_healthy else "degraded",
        "service": "ingest-agent",
        "database_connected": db_healthy,
        "message": "Service running" if not db_healthy else "All systems operational"
    }


@app.get("/")
async def root():
    return {"message": "Simple Ingest Agent", "status": "running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
