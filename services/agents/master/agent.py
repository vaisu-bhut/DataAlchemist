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
    _polling_task: Optional[Any]


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
        
        # Create a result container that can be shared
        result_container = {"result": None, "status": "pending"}
        
        # Start polling task BEFORE publishing request
        response_topic = f"{request_type}.response"
        state["_polling_task"] = asyncio.create_task(
            self._poll_for_response(correlation_id, response_topic, result_container)
        )
        
        # Store result container reference
        self.pending_requests[correlation_id] = result_container
        
        # Small delay to ensure polling starts
        await asyncio.sleep(0.1)
        
        # Now publish the request
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
        
        logger.info("Request published, polling started", correlation_id=correlation_id)
        state["status"] = "processing"
        return state
        
    async def _poll_for_response(self, correlation_id: str, response_topic: str, result_container: dict):
        """Background task to peek for response (doesn't remove until acknowledged)"""
        logger.info("Starting background peeking", correlation_id=correlation_id, topic=response_topic)
        
        async with httpx.AsyncClient() as client:
            poll_count = 0
            while True:
                try:
                    poll_count += 1
                    if poll_count % 10 == 0:
                        logger.debug(f"Peek attempt {poll_count}", correlation_id=correlation_id)
                    
                    # Use peek with correlation_id filter
                    response = await client.get(
                        f"{self.pubsub_url}/peek/{response_topic}",
                        params={"correlation_id": correlation_id},
                        timeout=5.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        message = data.get("message")
                        
                        if message:
                            logger.info("📨 Found message via peek", 
                                       correlation_id=correlation_id,
                                       message_keys=list(message.keys()))
                            
                            # Acknowledge to remove the message
                            ack_response = await client.post(
                                f"{self.pubsub_url}/acknowledge",
                                json={"topic": response_topic, "correlation_id": correlation_id},
                                timeout=5.0
                            )
                            
                            if ack_response.status_code == 200:
                                logger.info("✅ Message acknowledged and removed", correlation_id=correlation_id)
                                # Update the shared result container
                                result_container["result"] = message
                                result_container["status"] = "completed"
                                return
                            else:
                                logger.warning("Failed to acknowledge message", correlation_id=correlation_id)
                    
                    await asyncio.sleep(0.1)  # Fast polling
                    
                except asyncio.CancelledError:
                    logger.info("Polling cancelled", correlation_id=correlation_id)
                    return
                except Exception as e:
                    logger.error("Polling error", 
                                error=str(e), 
                                error_type=type(e).__name__,
                                correlation_id=correlation_id)
                    await asyncio.sleep(1)
    
    async def _wait_for_response(self, state: WorkflowState) -> WorkflowState:
        """Wait for the polling task to complete"""
        correlation_id = state["correlation_id"]
        
        logger.info("Waiting for response", correlation_id=correlation_id)
        
        polling_task = state.get("_polling_task")
        if not polling_task:
            state["error"] = "No polling task found"
            state["status"] = "failed"
            return state
        
        # Get the result container
        result_container = self.pending_requests.get(correlation_id)
        if not result_container:
            state["error"] = "No result container found"
            state["status"] = "failed"
            return state
        
        try:
            # Wait for polling task with timeout
            await asyncio.wait_for(polling_task, timeout=300.0)
            
            # Get result from the container
            if result_container["status"] == "completed" and result_container["result"]:
                state["result"] = result_container["result"]
                state["status"] = "completed"
                logger.info("✅ Response received successfully", correlation_id=correlation_id)
            else:
                state["error"] = "Polling completed but no response"
                state["status"] = "failed"
                logger.error("❌ No result in container after polling", 
                           correlation_id=correlation_id,
                           container_status=result_container["status"])
                
        except asyncio.TimeoutError:
            polling_task.cancel()
            state["error"] = "Request timeout"
            state["status"] = "failed"
            logger.error("⏱️ Request timeout", correlation_id=correlation_id)
        except Exception as e:
            polling_task.cancel()
            state["error"] = str(e)
            state["status"] = "failed"
            logger.error("❌ Wait failed", error=str(e), correlation_id=correlation_id)
        finally:
            # Cleanup
            if correlation_id in self.pending_requests:
                del self.pending_requests[correlation_id]
        
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
            error=None,
            _polling_task=None
        )
        
        # Run through LangGraph workflow
        final_state = await self.graph.ainvoke(initial_state)
        
        if final_state["error"]:
            raise Exception(final_state["error"])
            
        return final_state["result"]
