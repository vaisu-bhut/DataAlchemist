"""
Master Agent API with LangGraph
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/agents/master')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import structlog
import httpx

from agent import MasterAgent

logger = structlog.get_logger()

master_agent = None


class IngestRequest(BaseModel):
    conversations: List[Dict[str, Any]]


class ChatRequest(BaseModel):
    query: str
    customer_id: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global master_agent
    # Startup
    import os
    pubsub_url = os.getenv("PUBSUB_URL", "http://pubsub:8001")
    logger.info("Starting Master Agent with LangGraph", pubsub_url=pubsub_url)
    master_agent = MasterAgent(pubsub_url=pubsub_url)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Master Agent")


app = FastAPI(
    title="Master Agent with LangGraph",
    description="Orchestrator with state machine workflows",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/v1/ingest")
async def ingest(request: IngestRequest):
    """Ingest conversations through LangGraph workflow"""
    try:
        result = await master_agent.process_request(
            request_type="ingest",
            input_data={"conversations": request.conversations}
        )
        return result
    except Exception as e:
        logger.error("Ingest failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    """Chat query through LangGraph workflow"""
    try:
        result = await master_agent.process_request(
            request_type="chat",
            input_data={
                "query": request.query,
                "customer_id": request.customer_id
            }
        )
        return result
    except Exception as e:
        logger.error("Chat failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/{endpoint:path}")
async def get_analytics(endpoint: str):
    """Proxy analytics requests to analytics agent"""
    try:
        analytics_url = os.getenv("ANALYTICS_URL", "http://analytics-agent:8004")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{analytics_url}/api/v1/analytics/{endpoint}",
                timeout=30.0
            )
            return response.json()
    except Exception as e:
        logger.error("Analytics request failed", error=str(e), endpoint=endpoint)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "master-agent-langgraph",
        "version": "2.0.0"
    }


@app.get("/")
async def root():
    return {
        "message": "Master Agent with LangGraph",
        "status": "running",
        "version": "2.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
