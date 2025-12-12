"""
Analytics Agent - Provides metrics and statistics API
"""

from fastapi import FastAPI, HTTPException, Query
from contextlib import asynccontextmanager
import structlog
import sys
import os
from typing import Optional

# Add parent directories to path
sys.path.insert(0, "/app")
sys.path.insert(0, "/app/agents/analytics")

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
    except:
        pass

api_keys_json = os.getenv("API_KEYS")
if api_keys_json:
    try:
        api_keys = json.loads(api_keys_json)
        # Use lowercase to match pydantic Settings field names
        os.environ["gemini_api_key"] = api_keys.get("gemini_api_key", "")
        os.environ["gemini_model_name"] = api_keys.get(
            "gemini_model_name", "gemini-2.5-flash"
        )
        os.environ["gemini_embedding_model"] = api_keys.get(
            "gemini_embedding_model", "models/text-embedding-004"
        )
        os.environ["secret_key"] = api_keys.get("app_secret_key", "")
    except:
        pass

# Set defaults (lowercase to match pydantic Settings)
os.environ.setdefault("chunk_size", "2000")
os.environ.setdefault("similarity_threshold", "0.85")
os.environ.setdefault("confidence_threshold", "0.7")
os.environ.setdefault("max_retrieval_results", "10")

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
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {
        "message": "Analytics Agent",
        "status": "running",
        "endpoints": [
            "/api/v1/analytics/summary",
            "/api/v1/analytics/issues/distribution",
            "/api/v1/analytics/agents/performance",
            "/api/v1/analytics/customers",
            "/api/v1/analytics/customers/{customer_id}/issues",
            "/api/v1/analytics/resolution-time",
            "/api/v1/analytics/escalation",
        ],
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
        "database_connected": db_healthy,
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
    limit: int = Query(
        default=10, ge=1, le=100, description="Number of top issues to return"
    ),
):
    """Get top issues by occurrence"""
    try:
        issues = await analytics_service.get_issue_distribution(limit=limit)
        return {"total": len(issues), "issues": issues}
    except Exception as e:
        logger.error("Failed to get issue distribution", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/agents/performance")
async def get_agent_performance(
    limit: int = Query(
        default=10, ge=1, le=100, description="Number of top agents to return"
    ),
):
    """Get agent performance metrics"""
    try:
        agents = await analytics_service.get_agent_performance(limit=limit)
        return {"total": len(agents), "agents": agents}
    except Exception as e:
        logger.error("Failed to get agent performance", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/customers")
async def get_customers_list(
    limit: int = Query(
        default=20, ge=1, le=100, description="Number of customers to return"
    ),
):
    """Get list of customers with their conversation counts"""
    try:
        customers = await analytics_service.get_customers_list(limit=limit)
        return {"total": len(customers), "customers": customers}
    except Exception as e:
        logger.error("Failed to get customers list", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/customers/{customer_id}/issues")
async def get_customer_issue_history(customer_id: str):
    """Get all issues a specific customer has encountered"""
    try:
        history = await analytics_service.get_customer_issue_history(customer_id)
        return history
    except Exception as e:
        logger.error(
            "Failed to get customer issue history",
            error=str(e),
            customer_id=customer_id,
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/resolution-time")
async def get_resolution_time_stats():
    """Get resolution time statistics by issue type"""
    try:
        stats = await analytics_service.get_resolution_time_stats()
        return stats
    except Exception as e:
        logger.error("Failed to get resolution time stats", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/escalation")
async def get_escalation_analytics():
    """Get analytics on human escalation vs AI resolution"""
    try:
        analytics = await analytics_service.get_escalation_analytics()
        return analytics
    except Exception as e:
        logger.error("Failed to get escalation analytics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analytics/simulate-escalations")
async def simulate_escalations(count: int = 10):
    """Simulate escalations by marking some conversations as escalated (for testing)"""
    try:
        from core.database import Neo4jConnection

        neo4j_conn = Neo4jConnection()
        await neo4j_conn.connect()

        # Mark first N conversations as escalated
        query = """
        MATCH (c:Conversation)
        WHERE c.escalated_to_human IS NULL OR c.escalated_to_human = false
        WITH c LIMIT $count
        SET c.escalated_to_human = true
        RETURN count(c) as updated
        """

        result = await neo4j_conn.execute_query(query, {"count": count})
        updated_count = result[0]["updated"] if result else 0

        await neo4j_conn.close()

        return {
            "status": "success",
            "updated_conversations": updated_count,
            "message": f"Marked {updated_count} conversations as escalated to human",
        }
    except Exception as e:
        logger.error("Failed to simulate escalations", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8004)
