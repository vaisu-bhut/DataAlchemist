"""
In-memory PubSub Service - Direct Python async queues
"""
import asyncio
from collections import defaultdict
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class PubSubService:
    """In-memory message queue for agent communication"""
    
    def __init__(self):
        self.queues: Dict[str, asyncio.Queue] = defaultdict(lambda: asyncio.Queue())
        logger.info("PubSub service initialized")
    
    async def publish(self, topic: str, message: Dict[str, Any]):
        """Publish a message to a topic"""
        await self.queues[topic].put(message)
        logger.debug("Message published", topic=topic)
    
    async def poll(self, topic: str, timeout: float = 25.0) -> Optional[Dict[str, Any]]:
        """Poll for a message from a topic"""
        try:
            message = await asyncio.wait_for(
                self.queues[topic].get(),
                timeout=timeout
            )
            return message
        except asyncio.TimeoutError:
            return None
    
    def get_active_topics(self):
        """Get list of active topics"""
        return list(self.queues.keys())
