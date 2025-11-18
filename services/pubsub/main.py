"""
Lightweight Pub/Sub service for inter-agent communication
Stateless message routing between agents with peek/acknowledge pattern
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import structlog

from service import PubSubService

logger = structlog.get_logger()

app = FastAPI(title="Agent Pub/Sub Service", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pubsub service
pubsub_service = PubSubService()


class PublishRequest(BaseModel):
    topic: str
    message: Dict[str, Any]


class AcknowledgeRequest(BaseModel):
    topic: str
    correlation_id: str


@app.post("/publish")
async def publish(request: PublishRequest):
    """Publish a message to a topic"""
    try:
        await pubsub_service.publish(request.topic, request.message)
        return {"status": "published", "topic": request.topic}
    except Exception as e:
        logger.error("Publish failed", topic=request.topic, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/poll/{topic}")
async def poll(topic: str):
    """Poll for messages from a topic (removes message - for backward compatibility)"""
    try:
        message = await pubsub_service.poll(topic, timeout=25.0)
        return {"message": message}
    except Exception as e:
        logger.error("Poll failed", topic=topic, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/peek/{topic}")
async def peek(topic: str, correlation_id: Optional[str] = Query(None)):
    """Peek at messages without removing them - optionally filter by correlation_id"""
    try:
        message = await pubsub_service.peek(topic, correlation_id)
        return {"message": message}
    except Exception as e:
        logger.error("Peek failed", topic=topic, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/acknowledge")
async def acknowledge(request: AcknowledgeRequest):
    """Acknowledge and remove a specific message by correlation_id"""
    try:
        success = await pubsub_service.acknowledge(request.topic, request.correlation_id)
        return {"status": "acknowledged" if success else "not_found", "topic": request.topic}
    except Exception as e:
        logger.error("Acknowledge failed", topic=request.topic, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "pubsub",
        "version": "2.0.0",
        "active_topics": pubsub_service.get_active_topics()
    }


@app.get("/")
async def root():
    return {
        "message": "Agent Pub/Sub Service with Peek/Acknowledge", 
        "status": "running",
        "version": "2.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
