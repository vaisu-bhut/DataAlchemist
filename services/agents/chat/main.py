"""
Simple Chat Agent - Handles queries and retrieves from Neo4j
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
import httpx
import asyncio
import structlog
import sys

# Add parent directories to path
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/agents/chat')

# Load JSON secrets if they exist
try:
    from agents.shared.load_secrets import *
except:
    pass

logger = structlog.get_logger()

# Get PUBSUB_URL from environment or use default
import os
PUBSUB_URL = os.getenv("PUBSUB_URL", "http://pubsub:8001")

# Import after path is set
from core.database import Neo4jConnection
from services.retrieval_service import RetrievalService

neo4j_conn = None
retrieval_service = None
polling_task = None

# Log configuration on startup
logger.info("Chat Agent Configuration", pubsub_url=PUBSUB_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global neo4j_conn, retrieval_service, polling_task
    
    # Startup
    logger.info("Starting Chat Agent")
    
    # Wait a bit for other services to be ready
    await asyncio.sleep(2)
    
    # Connect to Neo4j with retries
    neo4j_conn = Neo4jConnection()
    for attempt in range(3):
        try:
            await neo4j_conn.connect()
            logger.info("Connected to Neo4j")
            break
        except Exception as e:
            logger.warning(f"Neo4j connection attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                await asyncio.sleep(2)
            else:
                logger.error("Failed to connect to Neo4j after 3 attempts")
                raise
    
    # Initialize retrieval service
    retrieval_service = RetrievalService(neo4j_conn)
    
    # Start polling for messages
    polling_task = asyncio.create_task(poll_for_requests())
    
    logger.info("Chat agent ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Chat Agent")
    if polling_task:
        polling_task.cancel()
    if neo4j_conn:
        await neo4j_conn.close()


app = FastAPI(title="Simple Chat Agent", version="1.0.0", lifespan=lifespan)


async def poll_for_requests():
    """Poll pub/sub for chat requests"""
    logger.info("Starting to poll for chat requests")
    
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # Poll for messages
                response = await client.get(
                    f"{PUBSUB_URL}/poll/chat.request",
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    message = data.get("message")
                    
                    if message:
                        logger.info("Received chat request", 
                                   correlation_id=message.get("correlation_id"))
                        await process_request(message)
                
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Polling error", error=str(e))
                await asyncio.sleep(1)


async def process_request(message: dict):
    """Process a chat request"""
    correlation_id = message.get("correlation_id")
    query = message.get("query")
    customer_id = message.get("customer_id", "anonymous")
    
    try:
        # Retrieve and generate response
        result = await retrieval_service.retrieve_and_respond(
            query=query,
            customer_id=customer_id,
            context=None
        )
        
        # Publish response
        response_message = {
            "correlation_id": correlation_id,
            "answer": result.get("response", "I couldn't find a relevant answer."),
            "sources": result.get("sources", []),
            "confidence": result.get("confidence", 0.0)
        }
        
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{PUBSUB_URL}/publish",
                json={"topic": "chat.response", "message": response_message},
                timeout=5.0
            )
        
        logger.info("Chat completed", 
                   correlation_id=correlation_id,
                   confidence=result.get("confidence", 0.0))
        
    except Exception as e:
        logger.error("Processing failed", 
                    correlation_id=correlation_id,
                    error=str(e))
        
        # Publish error response
        error_message = {
            "correlation_id": correlation_id,
            "answer": "I encountered an error processing your request.",
            "sources": [],
            "confidence": 0.0
        }
        
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{PUBSUB_URL}/publish",
                json={"topic": "chat.response", "message": error_message},
                timeout=5.0
            )


@app.get("/health")
async def health():
    db_healthy = await neo4j_conn.health_check() if neo4j_conn else False
    return {
        "status": "healthy" if db_healthy else "degraded",
        "service": "chat-agent",
        "database_connected": db_healthy
    }


@app.get("/")
async def root():
    return {"message": "Simple Chat Agent", "status": "running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
