"""
Master Agent with LangGraph - Orchestrator with state machine
"""
import asyncio
import uuid
from typing import TypedDict, Literal, Optional, Dict, Any
import structlog
import httpx

from langgraph.graph import StateGraph, END

logger = structlog.get_logger()


class WorkflowState(TypedDict):
    """State for master agent workflow"""
    request_type: Literal["ingest", "chat"]
    correlation_id: str
    input_data: Dict[str, Any]
    status: str
    result: Optional[Dict[str, Any]]
    error: Optional[str]


class MasterAgent:
    """Orchestrator agent with LangGraph workflow"""
    
    def __init__(self, pubsub_url: str = "http://pubsub:8001"):
        self.pubsub_url = pubsub_url
        self.pending_requests = {}
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow"""
        workflow = StateGraph(WorkflowState)
        
        # Define nodes
        workflow.add_node("route", self._route_request)
        workflow.add_node("wait_response", self._wait_for_response)
        workflow.add_node("complete", self._complete_request)
        
        # Define edges
        workflow.set_entry_point("route")
        workflow.add_edge("route", "wait_response")
        workflow.add_edge("wait_response", "complete")
        workflow.add_edge("complete", END)
        
        return workflow.compile()
        
    async def _route_request(self, state: WorkflowState) -> WorkflowState:
        """Route request to appropriate agent"""
        correlation_id = state["correlation_id"]
        request_type = state["request_type"]
        
        logger.info("Routing request", type=request_type, correlation_id=correlation_id)
        
        topic = f"{request_type}.request"
        message = {
            "correlation_id": correlation_id,
            **state["input_data"]
        }
        
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.pubsub_url}/publish",
                json={"topic": topic, "message": message},
                timeout=5.0
            )
        
        state["status"] = "processing"
        return state
        
    async def _wait_for_response(self, state: WorkflowState) -> WorkflowState:
        """Wait for agent response"""
        correlation_id = state["correlation_id"]
        request_type = state["request_type"]
        response_topic = f"{request_type}.response"
        
        logger.info("Waiting for response", correlation_id=correlation_id)
        
        # Poll for response with timeout
        start_time = asyncio.get_event_loop().time()
        timeout = 60.0
        
        async with httpx.AsyncClient() as client:
            while (asyncio.get_event_loop().time() - start_time) < timeout:
                try:
                    response = await client.get(
                        f"{self.pubsub_url}/poll/{response_topic}",
                        timeout=5.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        message = data.get("message")
                        
                        if message and message.get("correlation_id") == correlation_id:
                            state["result"] = message
                            state["status"] = "completed"
                            logger.info("Response received", correlation_id=correlation_id)
                            return state
                    
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error("Polling error", error=str(e))
                    await asyncio.sleep(1)
        
        # Timeout
        state["error"] = "Request timeout"
        state["status"] = "failed"
        logger.error("Request timeout", correlation_id=correlation_id)
        return state
        
    async def _complete_request(self, state: WorkflowState) -> WorkflowState:
        """Complete the workflow"""
        logger.info("Request completed", 
                   correlation_id=state["correlation_id"],
                   status=state["status"])
        return state
        
    async def process_request(self, request_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request through the LangGraph workflow"""
        correlation_id = str(uuid.uuid4())
        
        initial_state = WorkflowState(
            request_type=request_type,
            correlation_id=correlation_id,
            input_data=input_data,
            status="pending",
            result=None,
            error=None
        )
        
        # Run through LangGraph workflow
        final_state = await self.graph.ainvoke(initial_state)
        
        if final_state["error"]:
            raise Exception(final_state["error"])
            
        return final_state["result"]
