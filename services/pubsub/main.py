"""
Lightweight Pub/Sub service for inter-agent communication
Stateless message routing between agents
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
from collections import defaultdict
import asyncio
import structlog

logger = structlog.get_logger()

app = FastAPI(title="Agent Pub/Sub Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory message queues per topic
message_queues: Dict[str, asyncio.Queue] = defaultdict(lambda: asyncio.Queue())


class PublishRequest(BaseModel):
    topic: str
    message: Dict[str, Any]


@app.post("/publish")
async def publish(request: PublishRequest):
    """Publish a message to a topic"""
    try:
        await message_queues[request.topic].put(request.message)
        logger.info("Message published", topic=request.topic)
        return {"status": "published", "topic": request.topic}
    except Exception as e:
        logger.error("Publish failed", topic=request.topic, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/poll/{topic}")
async def poll(topic: str):
    """Poll for messages from a topic (long polling)"""
    try:
        # Wait for message with timeout
        message = await asyncio.wait_for(
            message_queues[topic].get(),
            timeout=25.0  # Long polling timeout
        )
        return {"message": message}
    except asyncio.TimeoutError:
        # No message available, return empty
        return {"message": None}
    except Exception as e:
        logger.error("Poll failed", topic=topic, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "pubsub",
        "active_topics": list(message_queues.keys())
    }


@app.get("/")
async def root():
    return {"message": "Agent Pub/Sub Service", "status": "running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
