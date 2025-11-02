from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import structlog
from contextlib import asynccontextmanager

from api.routes import ingest, chat
from core.database import Neo4jConnection
from core.config import settings

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Knowledge Engine API")
    neo4j_conn = Neo4jConnection()
    await neo4j_conn.connect()
    app.state.neo4j = neo4j_conn
    
    # Initialize database schema
    await neo4j_conn.initialize_schema()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Knowledge Engine API")
    await neo4j_conn.close()

app = FastAPI(
    title="Customer Conversation Knowledge Engine",
    description="AI-powered knowledge base from customer conversations",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingest.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    neo4j_conn = app.state.neo4j
    db_healthy = await neo4j_conn.health_check()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "service": "knowledge-engine",
        "database": "connected" if db_healthy else "disconnected"
    }

@app.get("/")
async def root():
    return {"message": "Customer Conversation Knowledge Engine API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)