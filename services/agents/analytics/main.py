"""
Analytics Agent - Provides metrics and statistics API
"""
from fastapi import FastAPI, HTTPException, Query
from contextlib import asynccontextmanager
import structlog
import sys
from typing import Optional

# Add parent directories to path
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/agents/analytics')

# Load JSON secrets if they exist
try:
    from agents.shared.load_secrets import *
except:
    pass

logger = structlog.get_logger()

from core.database import Neo4jConnection
from services.analytics_service import AnalyticsService
from models.schemas import MetricsSummary, IssueStats, AgentPerformance

neo4j_conn = None
analytics_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global neo4j_conn, analytics_service
    
    # Startup
    logger.info("Starting Analytics Agent")
    
    # Connect to Neo4j
    neo4j_conn = Neo4jConnection()
    try:
        await neo4j_conn.connect()
        logger.info("✅ Connected to Neo4j")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Neo4j: {e}")
        raise
    
    # Initialize analytics service
    analytics_service = AnalyticsService(neo4j_conn)
    logger.info("Analytics agent ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Analytics Agent")
    if neo4j_conn:
        await neo4j_conn.close()


app = FastAPI(
    title="Analytics Agent",
    version="1.0.0",
    description="Provides metrics and statistics for chat conversations",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {
        "message": "Analytics Agent",
        "status": "running",
        "endpoints": [
            "/api/v1/analytics/summary",
            "/api/v1/analytics/issues/distribution",
            "/api/v1/analytics/agents/performance"
        ]
    }


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
        "service": "analytics-agent",
        "database_connected": db_healthy
    }


@app.get("/api/v1/analytics/summary", response_model=MetricsSummary)
async def get_summary():
    """Get high-level summary metrics"""
    try:
        summary = await analytics_service.get_summary_metrics()
        
        # Enrich with top issues and agents
        summary.top_issues = await analytics_service.get_issue_distribution(limit=5)
        summary.top_agents = await analytics_service.get_agent_performance(limit=5)
        
        return summary
    except Exception as e:
        logger.error("Failed to get summary", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/issues/distribution")
async def get_issue_distribution(
    limit: int = Query(default=10, ge=1, le=100, description="Number of top issues to return")
):
    """Get top issues by occurrence"""
    try:
        issues = await analytics_service.get_issue_distribution(limit=limit)
        return {
            "total": len(issues),
            "issues": issues
        }
    except Exception as e:
        logger.error("Failed to get issue distribution", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/agents/performance")
async def get_agent_performance(
    limit: int = Query(default=10, ge=1, le=100, description="Number of top agents to return")
):
    """Get agent performance metrics"""
    try:
        agents = await analytics_service.get_agent_performance(limit=limit)
        return {
            "total": len(agents),
            "agents": agents
        }
    except Exception as e:
        logger.error("Failed to get agent performance", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
