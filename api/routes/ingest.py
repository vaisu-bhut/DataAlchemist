from fastapi import APIRouter, HTTPException, Depends
from fastapi.requests import Request
import structlog
from models.schemas import IngestRequest, IngestResponse
from services.ingestion_service import IngestionService

logger = structlog.get_logger()
router = APIRouter()

def get_ingestion_service(request: Request) -> IngestionService:
    return IngestionService(request.app.state.neo4j)

@router.post("/ingest", response_model=IngestResponse)
async def ingest_conversations(
    request: IngestRequest,
    ingestion_service: IngestionService = Depends(get_ingestion_service)
):
    """
    Ingest customer-agent conversations into the knowledge base.
    
    This endpoint:
    1. Sanitizes PII from conversations
    2. Extracts canonical issues and solutions using LLM
    3. Generates embeddings for semantic search
    4. Stores structured data in Neo4j with provenance
    5. Deduplicates similar issues
    """
    try:
        logger.info(f"Starting ingestion of {len(request.conversations)} conversations")
        
        if not request.conversations:
            raise HTTPException(status_code=400, detail="No conversations provided")
        
        # Validate conversations
        for conv in request.conversations:
            if not conv.conversation_id:
                raise HTTPException(status_code=400, detail="conversation_id is required")
            if not conv.customer_id:
                raise HTTPException(status_code=400, detail="customer_id is required")
            if not conv.messages:
                raise HTTPException(status_code=400, detail="messages are required")
        
        # Process conversations
        result = await ingestion_service.process_conversations(
            request.conversations, 
            request.batch_id
        )
        
        logger.info(f"Ingestion completed: {result.processed_count} processed, {result.failed_count} failed")
        
        return result
        
    except Exception as e:
        logger.error(f"Ingestion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.get("/ingest/status/{batch_id}")
async def get_ingestion_status(batch_id: str, request: Request):
    """Get status of a specific ingestion batch"""
    try:
        neo4j = request.app.state.neo4j
        
        # Query batch status
        query = """
        MATCH (c:Conversation {batch_id: $batch_id})
        RETURN count(c) as conversation_count,
               collect(DISTINCT c.id) as conversation_ids
        """
        
        result = await neo4j.execute_query(query, {'batch_id': batch_id})
        
        if not result:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        return {
            'batch_id': batch_id,
            'conversation_count': result[0]['conversation_count'],
            'conversation_ids': result[0]['conversation_ids']
        }
        
    except Exception as e:
        logger.error(f"Failed to get batch status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get batch status: {str(e)}")