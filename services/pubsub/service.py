"""
In-memory PubSub Service - Direct Python async queues with peek/acknowledge pattern
"""
import asyncio
from collections import defaultdict, deque
from typing import Dict, Any, Optional, Deque, List
import structlog
import time

logger = structlog.get_logger()


class PubSubService:
    """In-memory message queue for agent communication with peek/acknowledge pattern"""
    
    def __init__(self):
        # Store messages with timestamp for each topic
        self.messages: Dict[str, Deque[tuple[float, Dict[str, Any]]]] = defaultdict(deque)
        # Message TTL in seconds (5 minutes)
        self.message_ttl = 300
        logger.info("PubSub service initialized with peek/acknowledge pattern")
    
    async def publish(self, topic: str, message: Dict[str, Any]):
        """Publish a message to a topic"""
        timestamp = time.time()
        self.messages[topic].append((timestamp, message))
        logger.info("Message published", topic=topic, correlation_id=message.get("correlation_id"))
        
        # Clean old messages
        await self._cleanup_old_messages(topic)
    
    async def poll(self, topic: str, timeout: float = 25.0) -> Optional[Dict[str, Any]]:
        """Poll for a message from a topic - returns and removes the oldest message (for backward compatibility)"""
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            # Clean old messages first
            await self._cleanup_old_messages(topic)
            
            # Check if there are messages
            if self.messages[topic]:
                timestamp, message = self.messages[topic].popleft()
                logger.info("Message polled and removed", 
                           topic=topic, 
                           correlation_id=message.get("correlation_id"))
                return message
            
            # Wait a bit before checking again
            await asyncio.sleep(0.1)
        
        return None
    
    async def peek(self, topic: str, correlation_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Peek at messages without removing them - optionally filter by correlation_id"""
        await self._cleanup_old_messages(topic)
        
        # Look through all messages
        for timestamp, message in self.messages[topic]:
            if correlation_id is None or message.get("correlation_id") == correlation_id:
                logger.info("Message peeked (not removed)", 
                           topic=topic, 
                           correlation_id=message.get("correlation_id"))
                return message
        
        return None
    
    async def acknowledge(self, topic: str, correlation_id: str) -> bool:
        """Remove a specific message by correlation_id"""
        queue = self.messages[topic]
        
        # Find and remove the message with matching correlation_id
        for i, (timestamp, message) in enumerate(queue):
            if message.get("correlation_id") == correlation_id:
                # Remove this specific message
                del queue[i]
                logger.info("Message acknowledged and removed", 
                           topic=topic, 
                           correlation_id=correlation_id)
                return True
        
        logger.warning("Message not found for acknowledgment", 
                      topic=topic, 
                      correlation_id=correlation_id)
        return False
    
    async def _cleanup_old_messages(self, topic: str):
        """Remove messages older than TTL"""
        current_time = time.time()
        queue = self.messages[topic]
        
        # Remove old messages from the front
        while queue and (current_time - queue[0][0]) > self.message_ttl:
            old_timestamp, old_message = queue.popleft()
            logger.warning("Removed expired message", 
                          topic=topic,
                          age_seconds=current_time - old_timestamp,
                          correlation_id=old_message.get("correlation_id"))
    
    def get_active_topics(self):
        """Get list of active topics"""
        return list(self.messages.keys())
