from fastapi import APIRouter, HTTPException, Depends
from fastapi.requests import Request
import structlog
import uuid
from models.schemas import ChatQuery, ChatResponse
from services.retrieval_service import RetrievalService

logger = structlog.get_logger()
router = APIRouter()

def get_retrieval_service(request: Request) -> RetrievalService:
    return RetrievalService(request.app.state.neo4j)

@router.post("/chat", response_model=ChatResponse)
async def chat_query(
    query: ChatQuery,
    retrieval_service: RetrievalService = Depends(get_retrieval_service)
):
    """
    Answer customer queries using the knowledge base.
    
    This endpoint:
    1. Converts query to embedding
    2. Retrieves relevant issues/solutions from Neo4j
    3. Ranks candidates by similarity, quality, and human review
    4. Uses LLM to synthesize a response with citations
    5. Returns sourced answer with confidence score
    """
    try:
        query_id = str(uuid.uuid4())
        logger.info(f"Processing chat query {query_id} for customer {query.customer_id}")
        
        if not query.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Retrieve and generate response
        response_data = await retrieval_service.retrieve_and_respond(
            query.query,
            query.customer_id,
            query.context
        )
        
        # Build response
        chat_response = ChatResponse(
            response=response_data['response'],
            confidence=response_data['confidence'],
            sources=[
                {
                    'source_id': src['source_id'],
                    'conversation_id': src['conversation_id'],
                    'snippet': src['snippet'],
                    'relevance_score': src['relevance_score']
                }
                for src in response_data.get('sources', [])
            ],
            escalate_to_human=response_data.get('escalate_to_human', False),
            reasoning=response_data.get('reasoning'),
            query_id=query_id
        )
        
        logger.info(f"Query {query_id} completed with confidence {chat_response.confidence}")
        
        return chat_response
        
    except Exception as e:
        logger.error(f"Chat query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat query failed: {str(e)}")

@router.get("/chat/history/{customer_id}")
async def get_chat_history(customer_id: str, request: Request, limit: int = 10):
    """Get recent chat history for a customer"""
    try:
        neo4j = request.app.state.neo4j
        
        query = """
        MATCH (c:Conversation {customer_id: $customer_id})
        RETURN c.id as conversation_id,
               c.summary as summary,
               c.created_at as created_at
        ORDER BY c.created_at DESC
        LIMIT $limit
        """
        
        results = await neo4j.execute_query(query, {
            'customer_id': customer_id,
            'limit': limit
        })
        
        return {
            'customer_id': customer_id,
            'conversations': results
        }
        
    except Exception as e:
        logger.error(f"Failed to get chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")

@router.get("/knowledge/stats")
async def get_knowledge_stats(request: Request):
    """Get knowledge base statistics"""
    try:
        neo4j = request.app.state.neo4j
        
        # Use direct driver access for stats queries
        async with neo4j.driver.session(database="neo4j") as session:
            # Count conversations
            result = await session.run("MATCH (c:Conversation) RETURN count(c) as count")
            conv_records = []
            async for record in result:
                conv_records.append(record.data())
            
            # Count issues
            result = await session.run("MATCH (i:Issue) RETURN count(i) as count, count(CASE WHEN i.human_reviewed = true THEN 1 END) as reviewed")
            issue_records = []
            async for record in result:
                issue_records.append(record.data())
            
            # Count solutions
            result = await session.run("MATCH (s:Solution) RETURN count(s) as count, count(CASE WHEN s.human_reviewed = true THEN 1 END) as reviewed")
            solution_records = []
            async for record in result:
                solution_records.append(record.data())
        
        conv_result = conv_records
        issue_result = issue_records
        solution_result = solution_records
        
        total_conversations = conv_result[0]['count'] if conv_result else 0
        total_issues = issue_result[0]['count'] if issue_result else 0
        reviewed_issues = issue_result[0]['reviewed'] if issue_result else 0
        total_solutions = solution_result[0]['count'] if solution_result else 0
        reviewed_solutions = solution_result[0]['reviewed'] if solution_result else 0
        
        return {
            'total_conversations': total_conversations,
            'total_issues': total_issues,
            'total_solutions': total_solutions,
            'reviewed_issues': reviewed_issues,
            'reviewed_solutions': reviewed_solutions,
            'review_coverage': {
                'issues': reviewed_issues / max(total_issues, 1),
                'solutions': reviewed_solutions / max(total_solutions, 1)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get knowledge stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get knowledge stats: {str(e)}")